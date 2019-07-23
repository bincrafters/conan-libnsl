#include <rpcsvc/nis.h>

#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("nis_local_host: %s\n", nis_local_host());
    printf("nis_local_directory: %s\n", nis_local_directory());
    return 0;
}
