#include <osmocom/core/talloc.h>
#include <osmocom/core/utils.h>
#include <osmocom/core/linuxlist.h>

#include "rtp_provider.h"
#include "internal.h"


static LLIST_HEAD(g_providers);
static LLIST_HEAD(g_prov_instances);

void rtp_provider_register(struct rtp_provider *prov)
{
	llist_add_tail(&prov->list, &g_providers);
}

const struct rtp_provider *rtp_provider_find(const char *name)
{
	struct rtp_provider *p;
	llist_for_each_entry(p, &g_providers, list) {
		if (!strcmp(name, p->name))
			return p;
	}
	LOGP(DMAIN, LOGL_ERROR, "Couldn't find RTP provider '%s'\n", name);
	return NULL;
}

struct rtp_provider_instance *
rtp_provider_instance_alloc(void *ctx, const struct rtp_provider *provider, enum codec_type codec)
{
	struct rtp_provider_instance *pi;

	pi = talloc_zero(ctx, struct rtp_provider_instance);
	if (!pi)
		return NULL;

	pi->provider = provider;
	pi->codec = codec;
	llist_add_tail(&pi->list, &g_prov_instances);

	return pi;
}

void rtp_provider_instance_free(struct rtp_provider_instance *pi)
{
	llist_del(&pi->list);
	talloc_free(pi);
}

int rtp_provider_instance_gen_frame(struct rtp_provider_instance *pi, uint8_t *out, size_t out_size)
{
	OSMO_ASSERT(pi->provider);
	return pi->provider->rtp_gen(pi, out, out_size);
}
