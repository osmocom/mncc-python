OSMO_CFLAGS:=$(shell pkg-config --cflags libosmocore libosmoctrl libosmotrau)
OSMO_LIBS:=$(shell pkg-config --libs libosmocore libosmoctrl libosmotrau)

CFLAGS:= -g -Wall $(OSMO_CFLAGS)
LIBS:= $(OSMO_LIBS)

rtpsource: rtpsource.o ctrl_if.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)


%.o: %.c
	$(CC) $(CFLAGS) -o $@ -c $^

clean:
	@rm -f rtpsource *.o
