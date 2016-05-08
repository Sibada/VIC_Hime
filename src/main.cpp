#include <iostream>
#include <pthread.h>

#include "vic_hime.h"

using namespace std;

int main(int argc, char** argv) {

    int nthread = 1;
    string global_path;

    if(argc == 1) return 1;
    if(argc >= 2) global_path = argv[1];
    if(argc >=3)  nthread = atoi(argv[2]);
    if(nthread < 1) nthread = 1;

//    int ncell = 500;
//    int Nvegtype;
//
//    soil_con_struct** soilps = new soil_con_struct*[ncell];
//    veg_con_struct**  vegps  = new veg_con_struct*[ncell];
//
//    get_global(global_path);
//    Nvegtype = get_veg_lib("");
//    get_soil_params(soilps, 500, "");
//    get_veg_param(vegps, Nvegtype, soilps, ncell, "");
//
//    run_vic_multi_thread(soilps, vegps, NULL, ncell, 2);

    cout << "done.";
    return 0;
}
