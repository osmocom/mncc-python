#pragma once
#include <stdint.h>
#include <stdlib.h>
#include <osmocom/trau/osmo_ortp.h>
#include <osmocom/ctrl/control_if.h>

enum {
	DMAIN,
};

struct rtp_connection {
	struct llist_head list;

	struct osmo_rtp_socket *rtp_sock;
	char *cname;

	char *local_host;
	uint16_t local_port;

	char *remote_host;
	uint16_t remote_port;

	uint8_t rtp_pt;
};

struct rtpsource_state {
	struct llist_head connections;
	struct osmo_fd timer_ofd;
	struct ctrl_handle *ctrl;
};
extern struct rtpsource_state *g_rss;

struct rtp_connection *find_connection_by_cname(struct rtpsource_state *rss, const char *cname);

struct rtp_connection *create_connection(struct rtpsource_state *rss, const char *cname);

int connect_connection(struct rtp_connection *conn, const char *remote_host,
			uint16_t remote_port, uint8_t pt);

void delete_connection(struct rtp_connection *conn);


int rtpsource_ctrl_cmds_install(void);

#define CLOGP(conn, subsys, lvl, fmt, args ...) \
	LOGP(subsys, lvl, "[%s]: " fmt, (conn)->cname, ## args)
