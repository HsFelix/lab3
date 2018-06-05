# Análise referente às tarefas 4, 9 e 10 (filtro RL)

from errolab import *
from erros_mult import *
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
%matplotlib inline

nominal = unp.nominal_values

def pp(tabela):
    for linha in tabela:
        print(*linha,sep='   ')

# %%
dados_rc = np.loadtxt('pratica5/dados/rl.dat').T
_f, escVt, quadVt, escVr, quadVr, escdt, quaddt = dados_rc
_Vt = escVt*quadVt/2
_Vr = escVr*quadVr/2
_dt = escdt*quaddt

f = unp.uarray(_f, _f/1e3)
Vt = unp.uarray(_Vt, escVt/10)
Vr = unp.uarray(_Vr, escVr/10)
dt = unp.uarray(_dt, escdt/10)

_R = 47.2
_r = 14.6
_L = 46.1e-3

R = unc.ufloat(_R,err_o200(_R)) # escala de 200 ohms
r = unc.ufloat(_r,err_o200(_r)) # escala de 200 ohms
L = unc.ufloat(_L,err_i200m(_L)) # falta a função de erro do indutímetro

print("R = {}, r = {}, L = {}\n".format(R,r,L))

tabela = np.column_stack((f,Vt,Vr,1e6*dt))
print('f, Vt, Vr, dt')
pp(tabela)

FREQ_LIM = 210 # limite dos gráficos

#########################################################
# Análise da fase
#########################################################

# %%
print('\n\nANÁLISE DA FASE')

# espera-se que    aaa = L/(R+r)
_modelo1 = lambda w, aaa: np.arctan(w*aaa)
modelo1 = lambda w, aaa: unp.arctan(w*aaa)

omega = 2*np.pi*f
_omega = unp.nominal_values(omega)
phi = dt*omega-np.pi  # fase em radianos

# lista de índices dos ângulos que foram medidos errado
# (o suplementar)
flipar = (2,3,5,7,8,9)
for i in flipar:
    phi[i] = -phi[i]

phi_teorico = modelo1(omega,L/(R+r))
tabela = np.column_stack((phi*180/np.pi,phi_teorico*180/np.pi,
                    (phi-phi_teorico)*180/np.pi,
                    equiv(phi,phi_teorico)))
print('phi   \tphi_teorico\tdiferença')
pp(tabela)

ajuste_fase,mcov_fase = curve_fit(_modelo1,
    _omega, nominal(phi),
    [_L/(_R+_r)], unp.std_devs(phi))
_aaafase = ajuste_fase[0]
aaafase = unc.ufloat(_aaafase,np.sqrt(mcov_fase[0,0]))
print('L/(R+r) obtido:',aaafase)
print('L/(R+r) esperado:', L/(R+r))
print('equivalentes' if equiv(aaafase,L/(R+r)) else \
      'não equivalentes')

# %%
plt.figure(dpi=94)
# plt.figure(dpi=300)
f_lp = np.linspace(0.1,FREQ_LIM,200)
m = modelo1(2*np.pi*f_lp,L/(R+r))*180/np.pi
m_nom = unp.nominal_values(m)
m_err = unp.std_devs(m)
phi_g = phi*180/np.pi
plt.plot(f_lp,m_nom,zorder=1,
        label=r'$\varphi = \arctan(\omega L / (R+r))$')
plt.fill_between(f_lp,m_nom-2*m_err,m_nom+2*m_err,
                 alpha=0.4,zorder=0,
                 label=r'Intervalo de confiança ($\pm2\sigma$)')
plt.errorbar(nominal(f),nominal(phi_g),unp.std_devs(phi_g),
            fmt='.k',zorder=2,label='Dados experimentais')
plt.xlabel('Frequência (Hz)')
plt.ylabel('Fase (graus)')
plt.legend()
plt.title('Circuito RL: defasagem esperada da corrente')
plt.xlim(0,FREQ_LIM)
plt.show()
# plt.savefig('pratica5/graficos/fase_rl_teo.png',
            # bbox_inches='tight')

# %%
plt.figure(dpi=94)
# plt.figure(dpi=300)
f_lp = np.linspace(0.1,FREQ_LIM,200)
mfit = modelo1(2*np.pi*f_lp,aaafase)*180/np.pi
mfit_nom = unp.nominal_values(mfit)
mfit_err = unp.std_devs(mfit)
phi_g = phi*180/np.pi
plt.plot(f_lp,mfit_nom,zorder=1,
        color='green',label='Curva ajustada')
plt.fill_between(f_lp,mfit_nom-2*mfit_err,mfit_nom+2*mfit_err,
                 alpha=0.4,zorder=0,color='green',
                 label=r'Intervalo de confiança ($\pm2\sigma$)')
plt.errorbar(nominal(f),nominal(phi_g),unp.std_devs(phi_g),
            fmt='.k',zorder=2,label='Dados experimentais')
plt.xlabel('Frequência (Hz)')
plt.ylabel('Fase (graus)')
plt.legend()
plt.title('Circuito RL: defasagem da corrente')
plt.xlim(0,FREQ_LIM)
plt.show()
# plt.savefig('pratica5/graficos/fase_rl_fit.png',
            # bbox_inches='tight')

#########################################################
# Análise da função de transferência
#########################################################

# %%
print('ANÁLISE DA FUNÇÃO DE TRANSFERÊNCIA')

modelo2 = lambda omega, omega_0: (R/(R+r))*1/unp.sqrt(1+(omega/omega_0)**2)
_modelo2 = lambda omega, omega_0: (_R/(_R+_r))*1/np.sqrt(1+(omega/omega_0)**2)

m2 = modelo2(2*np.pi*f_lp,(R+r)/L)
m2_nom = nominal(m2)
m2_err = unp.std_devs(m2)
T = Vr/Vt
T_nom = nominal(T)
T_err = unp.std_devs(T)

ajuste_rc, mcov_rc = curve_fit(_modelo2, _omega, T_nom,
                               [(_R+_r)/_L], T_err)
_omega_0 = ajuste_rc[0]
omega_0 = unc.ufloat(_omega_0,np.sqrt(mcov_rc[0,0]))
print('omega_0 obtido:',omega_0)
print('esperado (multímetro):',(R+r)/L)
print('esperado (curva de fase):',1/aaafase)
print('obtido e multímetro',
    'equivalentes' if equiv(omega_0,(R+r)/L) else \
    'não equivalentes')
print('obtido e curva de fase',
    'equivalentes' if equiv(omega_0,1/aaafase) else \
    'não equivalentes')

m2fit = modelo2(2*np.pi*f_lp,omega_0)
m2fit_nom = nominal(m2fit)
m2fit_err = unp.std_devs(m2fit)

#%%
plt.figure(dpi=94)
# plt.figure(dpi=300)
plt.plot(f_lp, m2_nom, zorder=1,
        label=r'$|T(\omega)|=[1+(\omega L/(R+r))^2]^{-1/2}R/(R+r)$')
plt.fill_between(f_lp, m2_nom-2*m2_err, m2_nom+2*m2_err,
            alpha=0.4, zorder=0,
            label=r'Intervalo de confiança ($\pm2\sigma$)')
plt.errorbar(_f, T_nom, T_err,
            fmt='.k', zorder=2, label='Dados experimentais')

plt.legend(loc='lower left')
plt.title('Função de transferência (esperada)')
plt.xlabel('Frequência (Hz)')
plt.ylabel(r'$V_r \,/\, V_t$')
plt.ylim(0,1)
plt.xlim(0,FREQ_LIM)
plt.show()
# plt.savefig('pratica5/graficos/transf_rl_teo.png',
            # bbox_inches='tight')

# %%
plt.figure(dpi=94)
# plt.figure(dpi=300)
plt.plot(f_lp, m2fit_nom, zorder=1,
        color='green', label='Curva ajustada')
plt.fill_between(f_lp, m2fit_nom-2*m2fit_err,
                       m2fit_nom+2*m2fit_err,
            alpha=0.4, zorder=0, color='green',
            label=r'Intervalo de confiança ($\pm2\sigma$)')
plt.errorbar(_f, T_nom, T_err,
            fmt='.k', zorder=2, label='Dados experimentais')

plt.legend(loc='lower left')
plt.title('Função de transferência (ajuste)')
plt.xlabel('Frequência (Hz)')
plt.ylabel(r'$V_r \,/\, V_t$')
plt.ylim(0,1)
plt.xlim(0,FREQ_LIM)
plt.show()
# plt.savefig('pratica5/graficos/transf_rl_fit.png',
            # bbox_inches='tight')
