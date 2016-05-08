
/**************************************************************************
 *
 * 统计相关函数。
 * Some functions related to static.
 *
 * 2016-05-08
 *
 **************************************************************************/

#include "vic_hime.h"

/**************************************************************************
 *
 * 计算平均值。
 * Calculate mean value.
 *
 * 2016-05-08
 *
 **************************************************************************/
double mean(double* vec, int n){
    double sum = 0.0;
    for(int i = 0; i < n; i++) sum += vec[i];
    sum /= n;
    return sum;
}

/**************************************************************************
 *
 * 计算纳西效率系数。
 * Calculate Nusscy efficiency coefficient.
 *
 * 2016-05-08
 *
 **************************************************************************/

double calc_Nsc(double *sims, double *obss, int n) {
    double obs_mean = mean(obss, n);
    double a = 0.0, b = 0.0;
    for(int i = 0; i < n; i++) {
        a += (obss[i] - sims[i]) * (obss[i] - sims[i]);
        b += (obss[i] - obs_mean) * (obss[i] - obs_mean);
    }
    return 1 - a / b;
}

/**************************************************************************
 *
 * 计算相关系数。
 * Calculate Relative coefficient.
 *
 * 2016-05-08
 *
 **************************************************************************/
double calc_R(double *sims, double *obss, int n) {
    double ssum = 0.0, osum = 0.0, msum = 0.0;
    double s2sum = 0.0, o2sum = 0.0;

    for(int i = 0; i < n; i++) {
        ssum += sims[i];
        osum += obss[i];
        msum += sims[i] * obss[i];
        s2sum += sims[i] * sims[i];
        o2sum += obss[i] * obss[i];
    }
    double a = n * msum - ssum * osum;
    double b = (n * s2sum - ssum * ssum)
               * (n * o2sum - osum * osum);

    return a / sqrt(b);
}
/**************************************************************************
 *
 * 计算相对误差。
 * Calculate Relative error.
 *
 * 2016-05-08
 *
 **************************************************************************/
double calc_Re(double *sims, double *obss, int n){
    return mean(sims, n) / mean(obss, n) - 1;
}