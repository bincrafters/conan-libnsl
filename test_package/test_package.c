#include <rpc/rpc.h>

#define PROGNUM 100
#define VERSNUM 1

int main(int argc, char *argv[]) {
    svc_unreg(PROGNUM, VERSNUM);
    return 0;
}
