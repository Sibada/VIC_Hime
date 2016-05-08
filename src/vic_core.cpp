
#include <pthread.h>
#include <iostream>
#include "vic_hime.h"

using namespace std;

void* vic_thread(void* arg);

/**************************************************************************
 *
 * VIC多线程回调函数。
 * Multi-thread callback function.
 *
 * 2016-05-08
 *
 **************************************************************************/
void* vic_thread(void* arg){

    soil_con_struct* soil_param     =   NULL;
    veg_con_struct*  veg_param      =   NULL;
    lake_con_struct* lake_param     =   NULL;
    int              current_cell;

    lake_con_struct empty_lake_con;
    int status;

    /** 从参数包中取出参数  **/
    /** Take arguments out from argument package. **/
    arg_package* arg_pkg = (arg_package*)arg;
    soil_con_struct**   soil_params =   arg_pkg->soil_params;
    veg_con_struct**    veg_params  =   arg_pkg->veg_params;
    lake_con_struct**   lake_params =   arg_pkg->lake_params;
    int*                cell_id     =   arg_pkg->cell_id;
    int                 cell_num    =   arg_pkg->cell_num;
    pthread_mutex_t*    mutex_t       =   arg_pkg->mutex_t;

    while(true){
        /** 领取网格编号 **/
        /** Receipt cell id **/
        pthread_mutex_lock(mutex_t);
        current_cell = *cell_id;
        *cell_id = current_cell + 1;
        pthread_mutex_unlock(mutex_t);
        if(current_cell >= cell_num) break;

        soil_param = soil_params[current_cell];
        if (soil_param == NULL) continue;

        veg_param  = veg_params[current_cell];
        if(lake_params != NULL) lake_param = lake_params[current_cell];
        else lake_param = &empty_lake_con;

        status = run_a_cell(soil_param, veg_param, lake_param, NULL);
        cout << "Cell " << current_cell << " done.\n";

        if (status == ERROR) {
            cout << "Error at " << current_cell<<endl;
            break;
        }
    }
}

void run_vic_multi_thread(soil_con_struct** soilps, veg_con_struct** vegps, lake_con_struct** lakeps, int ncell, int thread_num) {

    int cell_id = 0;
    pthread_mutex_t mutex_t;

    arg_package arg;
    arg.cell_id = &cell_id;
    arg.lake_params = lakeps;
    arg.soil_params = soilps;
    arg.veg_params  = vegps;
    arg.cell_num    = ncell;
    arg.mutex_t     = &mutex_t;

    pthread_t threads[thread_num];
    pthread_mutex_init(&mutex_t, 0);

    for(int nt = 0; nt < thread_num; nt++)
        pthread_create(&threads[nt], 0, vic_thread, &arg);

    for(int nt = 0; nt < thread_num; nt++)
        pthread_join(threads[nt], 0);

    pthread_mutex_destroy(&mutex_t);
}
