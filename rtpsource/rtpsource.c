/* rtpsource program: RTP load generator
 *
 * This program binds a CTRL interface to 127.0.0.1:11111 and waits for
 * an external entity to issue CTRL commands, such as rtp_create, rtp_connect
 * and rtp_delete.  Those commands are used to create+bind, connect and destroy
 * local RTP connections.
 *
 * Each connection will send a RTP frame with dummy payload every 20ms.
 *
 * This is useful for load testing scenarios
 *
 * (C) 2020 by Harald Welte <laforge@gnumonks.org>
 *
 * All Rights Reserved
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */


#include <stdint.h>
#include <stdlib.h>
#include <inttypes.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <getopt.h>
#include <sys/signal.h>

#include <osmocom/core/linuxlist.h>
#include <osmocom/core/select.h>
#include <osmocom/core/application.h>
#include <osmocom/core/stats.h>
#include <osmocom/core/fsm.h>

#include <osmocom/ctrl/control_if.h>

#include <osmocom/trau/osmo_ortp.h>

#include "internal.h"


/* find a connection based on its CNAME */
struct rtp_connection *find_connection_by_cname(struct rtpsource_state *rss, const char *cname)
{
	struct rtp_connection *conn;
	llist_for_each_entry(conn, &rss->connections, list) {
		if (!strcmp(cname, conn->cname))
			return conn;
	}
	return NULL;
}

/* create a new RTP connection for given CNAME; includes binding of local RTP port */
struct rtp_connection *create_connection(struct rtpsource_state *rss, const char *cname)
{
	struct rtp_connection *conn;
	const char *host;
	int port;
	int rc;

	OSMO_ASSERT(!find_connection_by_cname(rss, cname));

	conn = talloc_zero(rss, struct rtp_connection);
	OSMO_ASSERT(conn);
	conn->cname = talloc_strdup(conn, cname);

	conn->rtp_sock = osmo_rtp_socket_create(conn, OSMO_RTP_F_POLL);
	OSMO_ASSERT(conn->rtp_sock);

	rc = osmo_rtp_socket_bind(conn->rtp_sock, rss->rtp_bind_ip, -1);
	OSMO_ASSERT(rc == 0);

	rc = osmo_rtp_get_bound_addr(conn->rtp_sock, &host, &port);
	OSMO_ASSERT(rc == 0);
	OSMO_ASSERT(port >= 0 && port <= 0xffff);
	conn->local_port = port;
	conn->local_host = talloc_strdup(conn, host);

	osmo_rtp_set_source_desc(conn->rtp_sock, conn->cname, "rtpsource", NULL, NULL,
				 NULL, "osmo-rtpsource", NULL);

	llist_add_tail(&conn->list, &rss->connections);

	CLOGP(conn, DMAIN, LOGL_INFO, "Created RTP connection; local=%s:%u\n",
		conn->local_host, conn->local_port);


	return conn;
}

/* connect a RTP connection to a given remote peer */
int connect_connection(struct rtp_connection *conn, const char *remote_host,
			uint16_t remote_port, uint8_t pt)
{
	int rc;

	conn->remote_host = talloc_strdup(conn, remote_host);
	conn->remote_port = remote_port;
	conn->rtp_pt = pt;

	rc = osmo_rtp_socket_connect(conn->rtp_sock, conn->remote_host, conn->remote_port);
	OSMO_ASSERT(rc == 0);
	rc = osmo_rtp_socket_set_pt(conn->rtp_sock, conn->rtp_pt);
	OSMO_ASSERT(rc == 0);

	CLOGP(conn, DMAIN, LOGL_INFO, "Connected RTP connection; remote=%s:%u\n",
		conn->remote_host, conn->remote_port);

	return 0;
}

/* delete a RTP connection */
void delete_connection(struct rtp_connection *conn)
{
	char *prefix = talloc_asprintf(conn, "[%s]: STATS: ", conn->cname);
	osmo_rtp_socket_log_stats(conn->rtp_sock, DMAIN, LOGL_INFO, prefix);
	talloc_free(prefix);
	osmo_rtp_socket_free(conn->rtp_sock);
	conn->rtp_sock = NULL;

	CLOGP(conn, DMAIN, LOGL_INFO, "Deleted RTP connection\n");

	llist_del(&conn->list);
	talloc_free(conn);
}




/* called every 20ms at timerfd expiration */
static int timerfd_cb(struct osmo_fd *ofd, unsigned int priv_nr)
{
	struct rtpsource_state *rss = ofd->data;
	struct rtp_connection *conn;
	uint64_t expire_count;
	int rc;

	/* read from timerfd: number of expirations of periodic timer */
	rc = read(ofd->fd, (void *) &expire_count, sizeof(expire_count));
	if (rc < 0 && errno == EAGAIN)
		return 0;

	if (expire_count > 1)
		LOGP(DMAIN, LOGL_ERROR, "Timer expire_count=%"PRIu64" != 1\n", expire_count);

	/* iterate over all RTP connections and send one frame each */
	llist_for_each_entry(conn, &rss->connections, list) {
		int i;
		/* TODO: have different sources (file+name, ...) */
		uint8_t payload[33];
		memset(payload, 0, sizeof(payload));
		payload[0] = (payload[0] & 0x0f) | 0xD0; /* mask in first four bit for FR */
		osmo_rtp_send_frame_ext(conn->rtp_sock, payload, sizeof(payload), 160, false);
		/* make sure RTP clock advances correctly, even if we missed transmit of some */
		for (i = 1; i < expire_count; i++)
			osmo_rtp_skipped_frame(conn->rtp_sock, 160);
	}
	return 0;
}

static const struct log_info_cat rtpsource_cat[] = {
	[DMAIN] = {
		.name = "DMAIN",
		.description ="Main Program",
		.enabled = 1,
		.loglevel = LOGL_INFO,
	},
};

const struct log_info rtpsource_log_info = {
	.filter_fn = NULL,
	.cat = rtpsource_cat,
	.num_cat = ARRAY_SIZE(rtpsource_cat),
};

struct rtpsource_state *g_rss;
static void *g_tall_ctx;

static void signal_handler(int signal)
{
	switch (signal) {
	case SIGABRT:
		/* in case of abort, we want to obtain a talloc report
		 * and then return to the caller, who will abort the process */
	case SIGUSR1:
		talloc_report_full(g_tall_ctx, stderr);
		break;
	default:
		break;
	}
}

static void handle_options(int argc, char **argv)
{
	while (1) {
		int option_index = 0, c;
		const struct option long_options[] = {
			{"rtp-bind-ip", 1, 0, 'r' },
			{ 0, 0, 0, 0}
		};
		c = getopt_long(argc, argv, "r:", long_options, &option_index);
		if (c == -1)
			break;

		switch (c) {
		case 'r':
			g_rss->rtp_bind_ip = optarg;
			break;
		default:
			break;
		}
	}
}

int main(int argc, char **argv)
{
	struct timespec interval = {
		.tv_sec = 0,
		.tv_nsec = 20*1000*1000, /* every 20ms */
	};
	int rc;

	signal(SIGUSR1, &signal_handler);
	signal(SIGABRT, &signal_handler);

	talloc_enable_null_tracking();
	g_tall_ctx = talloc_named_const(NULL, 1, "rtpsource");
	OSMO_ASSERT(g_tall_ctx);

	msgb_talloc_ctx_init(g_tall_ctx, 0);
	//osmo_signal_talloc_ctx_init(g_tall_ctx);
	osmo_init_logging2(g_tall_ctx, &rtpsource_log_info);
	osmo_fsm_log_timeouts(true);
	osmo_fsm_log_addr(true);
	osmo_stats_init(g_tall_ctx);
	osmo_rtp_init(g_tall_ctx);

	g_rss = talloc_zero(g_tall_ctx, struct rtpsource_state);
	OSMO_ASSERT(g_rss);
	INIT_LLIST_HEAD(&g_rss->connections);
	g_rss->rtp_bind_ip = "127.23.23.23";

	handle_options(argc, argv);

	/* Create CTRL interface */
	//g_rss->ctrl = ctrl_interface_setup_dynip(g_rss, ctrl_vty_get_bind_addr(), 11111, NULL);
	g_rss->ctrl = ctrl_interface_setup_dynip(g_rss, "127.0.0.1", 11111, NULL);
	OSMO_ASSERT(g_rss->ctrl);
	rc = rtpsource_ctrl_cmds_install();
	OSMO_ASSERT(rc == 0);

	/* create + register timerfd to expire every 20ms */
	g_rss->timer_ofd.fd = -1;
	rc = osmo_timerfd_setup(&g_rss->timer_ofd, timerfd_cb, g_rss);
	OSMO_ASSERT(rc == 0);

	rc = osmo_timerfd_schedule(&g_rss->timer_ofd, NULL, &interval);
	OSMO_ASSERT(rc == 0);

	while (1) {
		osmo_select_main(0);
	}
}
