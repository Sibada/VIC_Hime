#ifndef VIC_HIME_H
#define VIC_HIME_H

#include <math.h>
#include <vic.h>

/**************************************************************************
 *
 * 多线程回调函数的VIC API 参数包。
 * Multi-thread callback function's argument package of VIC API.
 *
 * 2016-05-08
 *
 **************************************************************************/
typedef struct{
    soil_con_struct**   soil_params;
    veg_con_struct**    veg_params;
    lake_con_struct**   lake_params;
    int*                cell_id;
    int                 cell_num;

    pthread_mutex_t*    mutex_t;
}arg_package;

void run_vic_multi_thread(soil_con_struct** soilps, veg_con_struct** vegps, lake_con_struct** lakeps, int ncell, int thread_num);

double mean(double* vec, int n);

double calc_Nsc(double *sims, double *obss, int n);

double calc_R(double *sims, double *obss, int n);

double calc_Re(double *sims, double *obss, int n);

#endif //VIC_HIME_VIC_HIME_H
