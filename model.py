
# coding: utf-8

# In[ ]:

from __future__ import division
from tkinter import W
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import numpy as np
import time
import random
import IPython
def print_np(x):
    print ("Type is %s" % (type(x)))
    print ("Shape is %s" % (x.shape,))
    # print ("Values are: \n%s" % (x))

class ODE_solution(object) :
    def __init__(self) :
        pass
    def setter(self,y,t) :
        self.y = y
        self.t = t

def RK4(odefun, tspan, y0,args,N_RK=10) :
    t = np.linspace(tspan[0],tspan[-1],N_RK)
    h = t[1] - t[0]
    iy = len(y0)
    y_sol = np.zeros((N_RK,iy))
    y_sol[0] = y0
    for idx in range(0,N_RK-1) :
        tk = t[idx]
        yk = y_sol[idx]
        k1 = odefun(tk,yk,*args)
        k2 = odefun(tk + h/2,yk + h/2*k1,*args)
        k3 = odefun(tk + h/2,yk + h/2*k2,*args)
        k4 = odefun(tk+h,yk+h*k3,*args)
        y_sol[idx+1] = yk + h/6 * (k1 + 2*k2 + 2*k3 + k4)

    sol = ODE_solution()
    sol.setter(y_sol.T,t)
    return sol

class OptimalcontrolModel(object) :
    def __init__(self,name,ix,iu,linearization) :
        self.name = name
        self.ix = ix
        self.iu = iu
        self.type_linearization = linearization

    def forward(self,x,u,idx=None):
        print("this is in parent class")
        pass

    def diff(self) :
        print("this is in parent class")
        pass

    def diff_numeric_central(self,x,u) :
        # state & input size
        ix = self.ix
        iu = self.iu
        
        ndim = np.ndim(x)
        if ndim == 1: # 1 step state & input
            N = 1
            x = np.expand_dims(x,axis=0)
            u = np.expand_dims(u,axis=0)
        else :
            N = np.size(x,axis = 0)
        
        # numerical difference
        h = pow(2,-18)
        eps_x = np.identity(ix)
        eps_u = np.identity(iu)

        # expand to tensor
        x_mat = np.expand_dims(x,axis=2)
        u_mat = np.expand_dims(u,axis=2)

        # diag
        x_diag = np.tile(x_mat,(1,1,ix))
        u_diag = np.tile(u_mat,(1,1,iu))

        # augmented = [x_aug x], [u, u_aug]
        x_aug_m = x_diag - eps_x * h
        x_aug_m = np.dstack((x_aug_m,np.tile(x_mat,(1,1,iu))))
        x_aug_m = np.reshape( np.transpose(x_aug_m,(0,2,1)), (N*(iu+ix),ix))

        u_aug_m = u_diag - eps_u * h
        u_aug_m = np.dstack((np.tile(u_mat,(1,1,ix)),u_aug_m))
        u_aug_m = np.reshape( np.transpose(u_aug_m,(0,2,1)), (N*(iu+ix),iu))

        # augmented = [x_aug x], [u, u_aug]
        x_aug_p = x_diag + eps_x * h
        x_aug_p = np.dstack((x_aug_p,np.tile(x_mat,(1,1,iu))))
        x_aug_p = np.reshape( np.transpose(x_aug_p,(0,2,1)), (N*(iu+ix),ix))

        u_aug_p = u_diag + eps_u * h
        u_aug_p = np.dstack((np.tile(u_mat,(1,1,ix)),u_aug_p))
        u_aug_p = np.reshape( np.transpose(u_aug_p,(0,2,1)), (N*(iu+ix),iu))

        # numerical difference
        f_change_m = self.forward(x_aug_m,u_aug_m,0)
        f_change_p = self.forward(x_aug_p,u_aug_p,0)
        f_change_m = np.reshape(f_change_m,(N,ix+iu,ix))
        f_change_p = np.reshape(f_change_p,(N,ix+iu,ix))
        f_diff = (f_change_p - f_change_m) / (2*h)
        f_diff = np.transpose(f_diff,[0,2,1])
        fx = f_diff[:,:,0:ix]
        fu = f_diff[:,:,ix:ix+iu]
        
        # return np.squeeze(fx), np.squeeze(fu)
        return fx,fu

    def diff_numeric(self,x,u) :
        # state & input size
        ix = self.ix
        iu = self.iu
        
        ndim = np.ndim(x)
        if ndim == 1: # 1 step state & input
            N = 1
            x = np.expand_dims(x,axis=0)
            u = np.expand_dims(u,axis=0)
        else :
            N = np.size(x,axis = 0)
        
        # numerical difference
        h = pow(2,-17)
        eps_x = np.identity(ix)
        eps_u = np.identity(iu)

        # expand to tensor
        x_mat = np.expand_dims(x,axis=2)
        u_mat = np.expand_dims(u,axis=2)

        # diag
        x_diag = np.tile(x_mat,(1,1,ix))
        u_diag = np.tile(u_mat,(1,1,iu))

        # augmented = [x_aug x], [u, u_aug]
        x_aug_m = x_diag - eps_x * 0
        x_aug_m = np.dstack((x_aug_m,np.tile(x_mat,(1,1,iu))))
        x_aug_m = np.reshape( np.transpose(x_aug_m,(0,2,1)), (N*(iu+ix),ix))

        u_aug_m = u_diag - eps_u * 0
        u_aug_m = np.dstack((np.tile(u_mat,(1,1,ix)),u_aug_m))
        u_aug_m = np.reshape( np.transpose(u_aug_m,(0,2,1)), (N*(iu+ix),iu))

        # augmented = [x_aug x], [u, u_aug]
        x_aug_p = x_diag + eps_x * h
        x_aug_p = np.dstack((x_aug_p,np.tile(x_mat,(1,1,iu))))
        x_aug_p = np.reshape( np.transpose(x_aug_p,(0,2,1)), (N*(iu+ix),ix))

        u_aug_p = u_diag + eps_u * h
        u_aug_p = np.dstack((np.tile(u_mat,(1,1,ix)),u_aug_p))
        u_aug_p = np.reshape( np.transpose(u_aug_p,(0,2,1)), (N*(iu+ix),iu))

        # numerical difference
        f_change_m = self.forward(x_aug_m,u_aug_m,0)
        f_change_p = self.forward(x_aug_p,u_aug_p,0)
        f_change_m = np.reshape(f_change_m,(N,ix+iu,ix))
        f_change_p = np.reshape(f_change_p,(N,ix+iu,ix))
        f_diff = (f_change_p - f_change_m) / (h)
        f_diff = np.transpose(f_diff,[0,2,1])
        fx = f_diff[:,:,0:ix]
        fu = f_diff[:,:,ix:ix+iu]
        
        return np.squeeze(fx), np.squeeze(fu)

    def diff_discrete_foh_serial(self,x,u,dtau,tf,N_RK=50) :
        ix = self.ix
        iu = self.iu

        ndim = np.ndim(x)
        if ndim == 1: # 1 step state & input
            N = 1
            x = np.expand_dims(x,axis=0)
            u = np.expand_dims(u,axis=0)
        else :
            N = np.size(x,axis = 0)

        def dvdt(t,V,um,up) :
            alpha = (dtau - t) / dtau
            beta = t / dtau
            u_ = alpha * um + beta * up
            x_ = V[:ix]
            Phi = V[ix:ix*ix + ix]
            Phi = Phi.reshape((ix,ix))
            Phi_inv = np.linalg.inv(Phi)
            f = self.forward(x_,u_).squeeze()
            if self.type_linearization == "numeric_central" :
                A,B = self.diff_numeric_central(x_,u_)
            elif self.type_linearization == "numeric_forward" :
                A,B = self.diff_numeric(x_,u_)
            elif self.type_linearization == "analytic" :
                A,B = self.diff(x_,u_)
            A,B = tf*A,tf*B
            A,B = np.squeeze(A),np.squeeze(B)
            dpdt = np.matmul(A,Phi).reshape((ix*ix)).reshape(-1)
            dbmdt = np.matmul(Phi_inv,B).reshape(-1) * alpha
            dbpdt = np.matmul(Phi_inv,B).reshape(-1) * beta
            dsdt = np.matmul(Phi_inv,f).transpose()
            # dzdt = np.matmul(Phi_inv,-np.matmul(A,x_) - np.matmul(B,u_))
            # dvdt = np.hstack((tf*f,dpdt,dbmdt,dbpdt,dsdt,dzdt))
            dvdt = np.hstack((tf*f,dpdt,dbmdt,dbpdt,dsdt))
            return dvdt
        
        idx_state = slice(0,ix)
        idx_A = slice(ix,ix+ix*ix)
        idx_Bm = slice(ix+ix*ix,ix+ix*ix+ix*iu)
        idx_Bp = slice(ix+ix*ix+ix*iu,ix+ix*ix+2*ix*iu)
        idx_s = slice(ix+ix*ix+2*ix*iu,ix+ix*ix+2*ix*iu+ix)
        # idx_z = slice(ix+ix*ix+2*ix*iu+ix,ix+ix*ix+2*ix*iu+ix+ix)

        A,Bm,Bp,s,z = [],[],[],[],[]
        x_prop = []

        for i in range(N) :
            # V0 = np.zeros(ix + ix*ix + 2*ix*iu + ix + ix)
            V0 = np.zeros(ix + ix*ix + 2*ix*iu + ix)
            V0[:ix] = x[i]
            V0[ix:ix*ix+ix] = np.eye(ix).flatten()

            # sol = solve_ivp(dvdt,(0,dtau),V0,args=(u[i],u[i+1]),method='RK45',rtol=1e-6,atol=1e-10)
            # sol = solve_ivp(dvdt,(0,dtau),V0,args=(u[i],u[i+1]))
            sol = RK4(dvdt,(0,dtau),V0,args=(u[i],u[i+1]),N_RK=N_RK)
            sol = sol.y[:,-1].reshape(-1)

            x_prop.append(sol[idx_state])
            A_mat = sol[idx_A].reshape((ix,ix)).squeeze()
            A.append(A_mat)
            Bm.append(np.matmul(A_mat,sol[idx_Bm].reshape((ix,iu))).squeeze())
            Bp.append(np.matmul(A_mat,sol[idx_Bp].reshape((ix,iu))).squeeze())
            s.append(np.matmul(A_mat,sol[idx_s]).squeeze())
            # z.append(np.matmul(A_mat,sol[idx_z]).squeeze())

        A = np.array(A)
        Bm = np.array(Bm)
        Bp = np.array(Bp)
        s = np.array(s)
        # z = np.array(z)
        x_prop = np.array(x_prop)
        z = x_prop - np.squeeze(A@np.expand_dims(x[0:N,:],2) +
                            Bm@np.expand_dims(u[0:N,:],2) + 
                            Bp@np.expand_dims(u[1:N+1,:],2) + 
                            np.expand_dims(tf*s,2))

        return A,Bm,Bp,s,z,x_prop


    def diff_discrete_foh(self,x,u,dtau,tf,N_RK=50) :
        # delT = self.delT
        ix = self.ix
        iu = self.iu

        ndim = np.ndim(x)
        if ndim == 1: # 1 step state & input
            N = 1
            x = np.expand_dims(x,axis=0)
            u = np.expand_dims(u,axis=0)
        else :
            N = np.size(x,axis = 0)

        def dvdt(t,V,um,up,length) :
            assert len(um) == len(up)
            assert len(um) == length
            alpha = (dtau - t) / dtau
            beta = t / dtau
            # print(alpha,beta)
            u = alpha * um + beta * up
            # IPython.embed()
            # V = V.reshape((length,ix + ix*ix + 2*ix*iu + ix + ix)).transpose()
            V = V.reshape((length,ix + ix*ix + 2*ix*iu + ix)).transpose()
            x = V[:ix].transpose()
            Phi = V[ix:ix*ix + ix]
            Phi = Phi.transpose().reshape((length,ix,ix))
            Phi_inv = np.linalg.inv(Phi)
            # Phi_inv = np.linalg.pinv(Phi)

            f = self.forward(x,u)
            if self.type_linearization == "numeric_central" :
                A,B = self.diff_numeric_central(x,u)
            elif self.type_linearization == "numeric_forward" :
                A,B = self.diff_numeric(x,u)
            elif self.type_linearization == "analytic" :
                A,B = self.diff(x,u)
            A,B = tf*A,tf*B
            dpdt = np.matmul(A,Phi).reshape((length,ix*ix)).transpose()
            dbmdt = np.matmul(Phi_inv,B).reshape((length,ix*iu)).transpose() * alpha
            # dbmdt = np.linalg.lstsq(Phi,B).reshape((length,ix*iu)).transpose() * alpha
            dbpdt = np.matmul(Phi_inv,B).reshape((length,ix*iu)).transpose() * beta
            dsdt = np.squeeze(np.matmul(Phi_inv,np.expand_dims(f,2))).transpose()
            # dzdt = np.squeeze(np.matmul(Phi_inv,-np.matmul(A,np.expand_dims(x,2)) - np.matmul(B,np.expand_dims(u,2)))).transpose()
            # dv = np.vstack((tf*f.transpose(),dpdt,dbmdt,dbpdt,dsdt,dzdt))
            dv = np.vstack((tf*f.transpose(),dpdt,dbmdt,dbpdt,dsdt))
            # IPython.embed()
            return dv.flatten(order='F')
        
        A0 = np.eye(ix).flatten()
        Bm0 = np.zeros((ix*iu))
        Bp0 = np.zeros((ix*iu))
        s0 = np.zeros(ix)
        # z0 = np.zeros(ix)
        # V0 = np.array([np.hstack((x[i],A0,Bm0,Bp0,s0,z0)) for i in range(N)]).transpose()
        V0 = np.array([np.hstack((x[i],A0,Bm0,Bp0,s0)) for i in range(N)]).transpose()
        V0_repeat = V0.flatten(order='F')

        # sol = solve_ivp(dvdt,(0,dtau),V0_repeat,args=(u[0:N],u[1:],N),method='RK45',rtol=1e-6,atol=1e-10)
        sol = RK4(dvdt,(0,dtau),V0_repeat,args=(u[0:N],u[1:],N),N_RK=N_RK)
        idx_state = slice(0,ix)
        idx_A = slice(ix,ix+ix*ix)
        idx_Bm = slice(ix+ix*ix,ix+ix*ix+ix*iu)
        idx_Bp = slice(ix+ix*ix+ix*iu,ix+ix*ix+2*ix*iu)
        idx_s = slice(ix+ix*ix+2*ix*iu,ix+ix*ix+2*ix*iu+ix)
        # idx_z = slice(ix+ix*ix+2*ix*iu+ix,ix+ix*ix+2*ix*iu+ix+ix)
        sol = sol.y[:,-1].reshape((N,-1))
        x_prop = sol[:,idx_state].reshape((-1,ix))
        A = sol[:,idx_A].reshape((-1,ix,ix))
        Bm = np.matmul(A,sol[:,idx_Bm].reshape((-1,ix,iu)))
        Bp = np.matmul(A,sol[:,idx_Bp].reshape((-1,ix,iu)))
        s = np.matmul(A,sol[:,idx_s].reshape((-1,ix,1))).squeeze()
        # z = np.matmul(A,sol[:,idx_z].reshape((-1,ix,1))).squeeze()
        z = x_prop - np.squeeze(A@np.expand_dims(x[0:N,:],2) +
                            Bm@np.expand_dims(u[0:N,:],2) + 
                            Bp@np.expand_dims(u[1:N+1,:],2) + 
                            np.expand_dims(tf*s,2))

        return A,Bm,Bp,s,z,x_prop

    def diff_discrete_foh_variational(self,x,u,dtau,tf,N_RK=50) :
        ix = self.ix
        iu = self.iu

        ndim = np.ndim(x)
        if ndim == 1: # 1 step state & input
            N = 1
            x = np.expand_dims(x,axis=0)
            u = np.expand_dims(u,axis=0)
        else :
            N = np.size(x,axis = 0)
        idx_state = slice(0,ix)
        idx_A = slice(ix,ix+ix*ix)
        idx_Bm = slice(ix+ix*ix,ix+ix*ix+ix*iu)
        idx_Bp = slice(ix+ix*ix+ix*iu,ix+ix*ix+2*ix*iu)
        idx_s = slice(ix+ix*ix+2*ix*iu,ix+ix*ix+2*ix*iu+ix)
        # idx_z = slice(ix+ix*ix+2*ix*iu+ix,ix+ix*ix+2*ix*iu+ix+ix)
        def dvdt(t,V,um,up,length) :
            assert len(um) == len(up)
            assert len(um) == length
            alpha = (dtau - t) / dtau
            beta = t / dtau
            u = alpha * um + beta * up
            # V = V.reshape((length,ix + ix*ix + 2*ix*iu + ix + ix)).transpose()
            V = V.reshape((length,ix + ix*ix + 2*ix*iu + ix)).transpose()
            x = V[:ix].transpose()
            Phi = V[ix:ix*ix + ix]
            Phi = Phi.transpose().reshape((length,ix,ix))
            x3 = V[idx_Bm].transpose().reshape(length,ix,iu)
            x4 = V[idx_Bp].transpose().reshape(length,ix,iu)
            x5 = V[idx_s].transpose().reshape(length,ix,1)
            # x6 = V[idx_z].transpose().reshape(length,ix,1)
            f = self.forward(x,u)
            if self.type_linearization == "numeric_central" :
                A,B = self.diff_numeric_central(x,u)
            elif self.type_linearization == "numeric_forward" :
                A,B = self.diff_numeric(x,u)
            elif self.type_linearization == "analytic" :
                A,B = self.diff(x,u)
            A,B = tf*A,tf*B
            dpdt = np.matmul(A,Phi).reshape((length,ix*ix)).transpose()
            dbmdt = (A@x3 + B*alpha).reshape((length,ix*iu)).transpose()
            dbpdt = (A@x4 + B*beta).reshape((length,ix*iu)).transpose()
            dsdt = np.squeeze(A@x5 + np.expand_dims(f,2)).transpose()
            # dzdt = np.squeeze(A@x6 - A@np.expand_dims(x,2) - B@np.expand_dims(u,2)).transpose()
            # dv = np.vstack((tf*f.transpose(),dpdt,dbmdt,dbpdt,dsdt,dzdt))
            dv = np.vstack((tf*f.transpose(),dpdt,dbmdt,dbpdt,dsdt))
            return dv.flatten(order='F')
        
        A0 = np.eye(ix).flatten()
        Bm0 = np.zeros((ix*iu))
        Bp0 = np.zeros((ix*iu))
        s0 = np.zeros(ix)
        # z0 = np.zeros(ix)
        # V0 = np.array([np.hstack((x[i],A0,Bm0,Bp0,s0,z0)) for i in range(N)]).transpose()
        V0 = np.array([np.hstack((x[i],A0,Bm0,Bp0,s0)) for i in range(N)]).transpose()
        V0_repeat = V0.flatten(order='F')

        # sol = solve_ivp(dvdt,(0,dtau),V0_repeat,args=(u[0:N],u[1:],N),rtol=1e-6,atol=1e-10)
        # sol = solve_ivp(dvdt,(0,dtau),V0_repeat,args=(u[0:N],u[1:],N))
        sol = RK4(dvdt,(0,dtau),V0_repeat,args=(u[0:N],u[1:],N),N_RK=N_RK)

        sol = sol.y[:,-1].reshape((N,-1))
        x_prop = sol[:,idx_state].reshape((-1,ix))
        A = sol[:,idx_A].reshape((-1,ix,ix))
        Bm = sol[:,idx_Bm].reshape((-1,ix,iu))
        Bp = sol[:,idx_Bp].reshape((-1,ix,iu))
        s = sol[:,idx_s].reshape((-1,ix,1)).squeeze()
        # z = sol[:,idx_z].reshape((-1,ix,1)).squeeze()
        z = x_prop - np.squeeze(A@np.expand_dims(x[0:N,:],2) +
                            Bm@np.expand_dims(u[0:N,:],2) + 
                            Bp@np.expand_dims(u[1:N+1,:],2) + 
                            np.expand_dims(tf*s,2))

        return A,Bm,Bp,s,z,x_prop