
#################################################
#    R-script for obtaining P50 and P88         #
#################################################

###### STEP 1 -  LOAD PACKAGES ######
library(tidyverse)
library(lubridate)
library(ggpubr)



###### STEP 2 - IMPORT DATASET  ######

data<- read_csv("DataS1/venation_function/hydraulics/UCBG_venation_VC.csv")
glimpse(data)

###### STEP 3 - FIT VULNERABILITY CURVES ######
spp_target <- "Cus_spi" # type the spp_code here
dt_spp<- data %>% filter (spp_code == spp_target) 
glimpse(dt_spp)

### Fit exponential curve -------------------------------
model <-function (A,B,Yo,psi){Yo+A*exp(-B*psi)} # Kleaf = yO +A*exp(-B*psi), psi is either Pf or P_lowest
likelisum<-function(pars,psi,observed)
{
  A<-pars[[1]]
  B<-pars[[2]]
  Yo<-pars[[3]]
  sd<-pars[[4]]
  predicted <-model(A,B,Yo,psi)
  likelisum<-sum(dnorm(observed,predicted,sd,log=T))
  
}

pars <- list(A=2,B=2,Yo=2,sd=2) # select initial values for all parameters

# 1st optim using SANN method (global optimization) 

res<-optim(pars,likelisum,method="SANN",control=list(fnscale=-1,maxit=5000),hessian=T,psi=dt_spp$Pf,observed=dt_spp$Kleaf_area)

### pars = initial parameters values 
### likelisum = function to be optimized (exponential in this case)
### method ="SANN" specifies a function to generate a new candidate point;It is not a general-purpose method but can be very useful in getting to a good value on a very rough surface. 
### control = fnscale= scale to be applied during the optim process, negative values indicate maximization (rather than minimization)
###         = maxit = maximum number of iterations 
### hessian = true to return the Hessel matrix
### psi = final leaf water potential values (Pf)
### observed = leaf water conductance values corrected for leaf area (Kleaf)

pars <-list(A=res$par[1], B=res$par[2], Yo=res$par[3], sd=res$par[4])

res ## results of 1st optim
### par = parameters values after 1st optim
### value = Kleaf value when applying the par values above
### counts = number of iterations?
### convergence = 0 indicates convergence 
### hessian = symmetric matrix giving an estimate of the Hessian at the solution found. 
###           used to calculate sd values          

# 2nd optim Nelder-Mead (local optimization) 

res<-optim(pars,likelisum,method="Nelder-Mead",control=list(fnscale=-1,maxit=5000),hessian=T,psi=dt_spp$Pf,observed=dt_spp$Kleaf_area)

# Calculate AIC
# log likelihood
res$value
#AIC : -2LL + 2*parameters (incl nuisance, i.e.,sd)
AIC<- -2*res$value + 2*4
#AIC corrected for low sample size: -2LL + (2*n*parameters (incl nuisance, i.e.,sd)/(n-parameters-1))
AICcorr <- -2*res$value + 2*length(dt_spp$Kleaf_area)*4/(length(dt_spp$Kleaf_area)-4-1)

# Residual analysis
# expected values
expected<-model(res$par[1], res$par[2], res$par[3], dt_spp$Pf)
slope <-sum(expected*dt_spp$Kleaf_area)/sum(dt_spp$Kleaf_area^2)
# calculate R-squared
rsq <- 1-(sum((dt_spp$Kleaf_area-expected)^2)/sum((dt_spp$Kleaf_area-mean(dt_spp$Kleaf_area))^2))
# residuals
resid<-(expected-dt_spp$Kleaf_area)
# histogram of residuals
hist (resid) # check if the distribution is normal (norm) or not (anorm)

# parameter values
res$par
A<-as.numeric(res$par[1])
B<-as.numeric(res$par[2])
Yo<-as.numeric(res$par[3])

# Calculate P50 and P88
Kmax<- Yo + A * exp (- (B * 0))
P50 <- (-1/B)* log(((Kmax *0.5)-Yo)/A)
P88 <- (-1/B)* log(((Kmax *0.12)-Yo)/A)

# Uncertainty around parameters


# calculate sd around each parameter using the hessian matrix
sterror<-sqrt(diag(solve(-1*res$hessian)))
Asd<- as.numeric(sterror[1])
Bsd<- as.numeric(sterror[2])
Yosd<- as.numeric(sterror[3])
Alow<- A - Asd
Aup<- A + Asd
Blow<- B - Bsd
Bup<- B + Bsd
Yolow<- Yo - Yosd
Youp<- Yo + Yosd

# obtain the VC curve and the uncertainty around it
## exponential function = (YO +A)*exp(-B*x)

myfun <- function(x) Yo+A *exp(-B*x) # mean curve
myfun_low1 <- function(x) Yo+Alow *exp(-B*x) # low A
myfun_low2 <- function(x) Yo+A *exp(-Blow*x) # low B
myfun_low3 <- function(x) Yolow+A *exp(-B*x) # low Yo
myfun_up1 <- function(x) B+Aup *exp(-B*x) # up A
myfun_up2 <- function(x) Bup+A *exp(-Bup*x) # up B
myfun_up3 <- function(x) B+A *exp(-B*x) # up Yo


# plot VC curve using ggplot
dev.off()
p1<-ggplot(dt_spp, aes(x=Pf, y=Kleaf_area)) +
  geom_point(size=4, shape=1, alpha = .8, color = "black", stroke = 1)+
  stat_function(fun = myfun_low1, color = "grey", size = 1.5)+
  stat_function(fun = myfun_low2, color = "grey", size = 1.5)+
  stat_function(fun = myfun_low3, color = "grey", size = 1.5)+
  stat_function(fun = myfun_up1, color = "grey", size = 1.5)+
  stat_function(fun = myfun_up2, color = "grey", size = 1.5)+
  stat_function(fun = myfun_up3, color = "grey", size = 1.5)+
  stat_function(fun = myfun, color = "black", size = 1)+
  labs(title = spp_target, y= "Kleaf (mmol m-2 s-1 MPa-1)", x= "Leaf water potential (-MPa)")+
  theme_classic()+
  theme(
    axis.title.x = element_text(size=14),
    axis.title.y = element_text(size=14),
    axis.text.x = element_text(size=14, color = "black"),
    axis.text.y = element_text(size=14, color = "black"),
    axis.line = element_line(size = 1, linetype = "solid")
  )+geom_vline(xintercept= P50, linetype="solid", color = "orange", lwd = 1)+
  geom_vline(xintercept= P88, linetype="solid", color = "red", lwd = 1);p1

#save plot
#ggsave(paste0(spp_target,"_P50_exponential.png"), width = 10, height = 10, dpi = 300, units = "cm", device='png')

### Fit logistic curve -------------------
model <-function (A,B,Xo,psi){A/(1+((psi/Xo)^B))}
likelisum<-function(pars,psi,observed)
{
  A<-pars[[1]]
  B<-pars[[2]]
  Xo<-pars[[3]]
  sd<-pars[[4]]
  predicted <-model(A,B,Xo,psi)
  likelisum<-sum(dnorm(observed,predicted,sd,log=T))
  
}

pars <- list(A=2,B=2,Xo=2,sd=2) # select initial values for all parameters

# 1st optim using SANN method (global optimization) 

res<-optim(pars,likelisum,method="SANN",control=list(fnscale=-1,maxit=5000),hessian=T,psi=dt_spp$Pf,observed=dt_spp$Kleaf_area)
pars <-list(A=res$par[1], B=res$par[2], Xo=res$par[3], sd=res$par[4])

res ## results of 1st optim

# 2nd optim Nelder-Mead (local optimization) 

res<-optim(pars,likelisum,method="Nelder-Mead",control=list(fnscale=-1,maxit=5000),hessian=T,psi=dt_spp$Pf,observed=dt_spp$Kleaf_area)

# Calculate AIC
# log likelihood
res$value
#AIC : -2LL + 2*parameters (incl nuisance, i.e.,sd)
AIC<- -2*res$value + 2*4
#AIC corrected for low sample size: -2LL + (2*n*parameters (incl nuisance, i.e.,sd)/(n-parameters-1))
AICcorr <- -2*res$value + 2*length(dt_spp$Kleaf_area)*4/(length(dt_spp$Kleaf_area)-4-1)

# Residual analysis
# expected values
expected<-model(res$par[1], res$par[2], res$par[3], dt_spp$Pf)
slope <-sum(expected*dt_spp$Kleaf_area)/sum(dt_spp$Kleaf_area^2)
# calculate R-squared
rsq <- 1-(sum((dt_spp$Kleaf_area-expected)^2)/sum((dt_spp$Kleaf_area-mean(dt_spp$Kleaf_area))^2))
# residuals
resid<-(expected-dt_spp$Kleaf_area)
# histogram of residuals
hist (resid) # check if the distribution is normal (norm) or not (anorm)

# parameter values
res$par
A<-as.numeric(res$par[1])
B<-as.numeric(res$par[2])
Xo<-as.numeric(res$par[3])

# Calculate P50 and P88
Kmax <- A
P88 <- Xo * (A/(Kmax*0.12)-1)^(1/B)
P50 <-  Xo * (A/(Kmax*0.5)-1)^(1/B)

# Uncertainty around parameters
# calculate sd around each parameter using the hessian matrix
sterror<-sqrt(diag(solve(-1*res$hessian)))
Asd<- as.numeric(sterror[1])
Bsd<- as.numeric(sterror[2])
Xosd<- as.numeric(sterror[3])
Alow<- A - Asd
Aup<- A + Asd
Blow<- B - Bsd
Bup<- B + Bsd
Xolow<- Xo - Yosd
Xoup<- Xo + Yosd

# obtain the VC curve and the uncertainty around it
## logistic function = A/(1+((psi/Yo)^B))
myfun <- function(x) A/(1+((x/Xo)^B)) # mean curve
myfun_low1 <- function(x) Alow/(1+((x/Xo)^B)) # low A
myfun_low2 <- function(x) A/(1+((x/Xo)^Blow)) # low B
myfun_low3 <- function(x) A/(1+((x/Xolow)^B)) # low Yo
myfun_up1 <- function(x) Aup/(1+((x/Xo)^B)) # up A
myfun_up2 <- function(x) A/(1+((x/Xo)^Bup)) # up B
myfun_up3 <- function(x) A/(1+((x/Xoup)^B)) # up Yo


# plot VC curve using ggplot
p1<-ggplot(dt_spp, aes(x=Pf, y=Kleaf_area)) +
  geom_point(size=4, shape=1, alpha = .8, color = "black", stroke = 1)+
  stat_function(fun = myfun_low1, color = "grey", size = 1.5)+
  stat_function(fun = myfun_low2, color = "grey", size = 1.5)+
  stat_function(fun = myfun_low3, color = "grey", size = 1.5)+
  stat_function(fun = myfun_up1, color = "grey", size = 1.5)+
  stat_function(fun = myfun_up2, color = "grey", size = 1.5)+
  stat_function(fun = myfun_up3, color = "grey", size = 1.5)+
  stat_function(fun = myfun, color = "black", size = 1)+
  labs(title = spp_target, y= "Kleaf (mmol m-2 s-1 MPa-1)", x= "Leaf water potential (-MPa)")+
  theme_classic()+
  theme(
    axis.title.x = element_text(size=14),
    axis.title.y = element_text(size=14),
    axis.text.x = element_text(size=14, color = "black"),
    axis.text.y = element_text(size=14, color = "black"),
    axis.line = element_line(size = 1, linetype = "solid")
  )+geom_vline(xintercept= P50, linetype="solid", color = "orange", lwd = 1)+
  geom_vline(xintercept= P88, linetype="solid", color = "red", lwd = 1);p1

#save plot
#ggsave(paste0(spp_target,"_P50_logistic.png"), width = 10, height = 10, dpi = 300, units = "cm", device='png')


### Fit sigmoidal curve -------------------
model <-function (A,B,Xo,psi){A/(1+exp(-((psi-Xo)/B)))} 
likelisum<-function(pars,psi,observed)
{
  A<-pars[[1]]
  B<-pars[[2]]
  Xo<-pars[[3]]
  sd<-pars[[4]]
  predicted <-model(A,B,Xo,psi)
  likelisum<-sum(dnorm(observed,predicted,sd,log=T))
  
}
pars <- list(A=10,B=-1,Xo=-1,sd=2)# select initial values for all parameters

# 1st optim using SANN method (global optimization) 

res<-optim(pars,likelisum,method="SANN",control=list(fnscale=-1,maxit=5000),hessian=T,psi=dt_spp$Pf,observed=dt_spp$Kleaf_area)
pars <-list(A=res$par[1], B=res$par[2], Xo=res$par[3], sd=res$par[4])

res ## results of 1st optim

# 2nd optim Nelder-Mead (local optimization) 

res<-optim(pars,likelisum,method="Nelder-Mead",control=list(fnscale=-1,maxit=5000),hessian=T,psi=dt_spp$Pf,observed=dt_spp$Kleaf_area)

# Calculate AIC
# log likelihood
res$value
#AIC : -2LL + 2*parameters (incl nuisance, i.e.,sd)
AIC<- -2*res$value + 2*4
#AIC corrected for low sample size: -2LL + (2*n*parameters (incl nuisance, i.e.,sd)/(n-parameters-1))
AICcorr <- -2*res$value + 2*length(dt_spp$Kleaf_area)*4/(length(dt_spp$Kleaf_area)-4-1)

# Residual analysis
# expected values
expected<-model(res$par[1], res$par[2], res$par[3], dt_spp$Pf)
slope <-sum(expected*dt_spp$Kleaf_area)/sum(dt_spp$Kleaf_area^2)
# calculate R-squared
rsq <- 1-(sum((dt_spp$Kleaf_area-expected)^2)/sum((dt_spp$Kleaf_area-mean(dt_spp$Kleaf_area))^2))
# residuals
resid<-(expected-dt_spp$Kleaf_area)
# histogram of residuals
hist (resid) # check if the distribution is normal (norm) or not (anorm)

# parameter values
res$par
A<-as.numeric(res$par[1])
B<-as.numeric(res$par[2])
Xo<-as.numeric(res$par[3])

# Calculate P50 and P88
Kmax <- A/(1+ exp (-(0-Xo/B)))
P88 <- -B*log(A/(Kmax*0.12)-1)+Xo
P50 <-  -B*log(A/(Kmax*0.5)-1)+Xo

# Uncertainty around parameters
# calculate sd around each parameter using the hessian matrix
sterror<-sqrt(diag(solve(-1*res$hessian)))
Asd<- as.numeric(sterror[1])
Bsd<- as.numeric(sterror[2])
Yosd<- as.numeric(sterror[3])
Alow<- A - Asd
Aup<- A + Asd
Blow<- B - Bsd
Bup<- B + Bsd
Xolow<- Xo - Yosd
Xoup<- Xo + Yosd

# obtain the VC curve and the uncertainty around it
## sigmoidal function = A/(1+exp(-((x-Xo)/B)))
myfun <- function(x) A/(1+exp(-((x-Xo)/B))) # mean curve
myfun_low1 <- function(x) Alow/(1+exp(-((x-Xo)/B))) # low A
myfun_low2 <- function(x) A/(1+exp(-((x-Xo)/Blow))) # low B
myfun_low3 <- function(x) A/(1+exp(-((x-Xolow)/B))) # low Yo
myfun_up1 <- function(x) Aup/(1+exp(-((x-Xo)/B))) # up A
myfun_up2 <- function(x) A/(1+exp(-((x-Xo)/Bup)))# up B
myfun_up3 <- function(x) A/(1+exp(-((x-Xoup)/B))) # up Yo


# plot VC curve using ggplot
p1<-ggplot(dt_spp, aes(x=Pf, y=Kleaf_area)) +
  geom_point(size=4, shape=1, alpha = .8, color = "black", stroke = 1)+
  stat_function(fun = myfun_low1, color = "grey", size = 1.5)+
  stat_function(fun = myfun_low2, color = "grey", size = 1.5)+
  stat_function(fun = myfun_low3, color = "grey", size = 1.5)+
  stat_function(fun = myfun_up1, color = "grey", size = 1.5)+
  stat_function(fun = myfun_up2, color = "grey", size = 1.5)+
  stat_function(fun = myfun_up3, color = "grey", size = 1.5)+
  stat_function(fun = myfun, color = "black", size = 1)+
  labs(title = spp_target, y= "Kleaf (mmol m-2 s-1 MPa-1)", x= "Leaf water potential (-MPa)")+
  theme_classic()+
  theme(
    axis.title.x = element_text(size=14),
    axis.title.y = element_text(size=14),
    axis.text.x = element_text(size=14, color = "black"),
    axis.text.y = element_text(size=14, color = "black"),
    axis.line = element_line(size = 1, linetype = "solid")
  )+geom_vline(xintercept= P50, linetype="solid", color = "orange", lwd = 1)+
  geom_vline(xintercept= P88, linetype="solid", color = "red", lwd = 1);p1

#save plot
#ggsave(paste0(spp_target,"_P50_sigmoidal.png"), width = 10, height = 10, dpi = 300, units = "cm", device='png')



### Fit linear curve -------------------
model <-function (A,B,psi){A*(psi)+B} # Kleaf = A*psi + B, where A = slope, B = Y0 = Kmax = Kleaf value when psi =0
likelisum<-function(pars,psi,observed)
{
  A<-pars[[1]]
  B<-pars[[2]]
  sd<-pars[[3]]
  predicted <-model(A,B,psi)
  likelisum<-sum(dnorm(observed,predicted,sd,log=T))
}

pars <- list(A=2,B=2,sd=2) # select initial values for all parameters

# 1st optim using SANN method (global optimization) 

res<-optim(pars,likelisum,method="SANN",control=list(fnscale=-1,maxit=5000),hessian=T,psi=dt_spp$Pf,observed=dt_spp$Kleaf_area)
pars <-list(A=res$par[1], B=res$par[2],sd=res$par[3])

res ## results of 1st optim

# 2nd optim Nelder-Mead (local optimization) 

res<-optim(pars,likelisum,method="Nelder-Mead",control=list(fnscale=-1,maxit=5000),hessian=T,psi=dt_spp$Pf,observed=dt_spp$Kleaf_area)

# Calculate AIC
# log likelihood
res$value
#AIC : -2LL + 2*parameters (incl nuisance, i.e.,sd)
AIC<- -2*res$value + 2*3
#AIC corrected for low sample size: -2LL + (2*n*parameters (incl nuisance, i.e.,sd)/(n-parameters-1))
AICcorr <- -2*res$value + 2*length(dt_spp$Kleaf_area)*3/(length(dt_spp$Kleaf_area)-3-1)

# Residual analysis
# expected values
expected<-model(res$par[1], res$par[2],dt_spp$Pf)
slope <-sum(expected*dt_spp$Kleaf_area)/sum(dt_spp$Kleaf_area^2)
# calculate R-squared
rsq <- 1-(sum((dt_spp$Kleaf_area-expected)^2)/sum((dt_spp$Kleaf_area-mean(dt_spp$Kleaf_area))^2))
# residuals
resid<-(expected-dt_spp$Kleaf_area)
# histogram of residuals
hist (resid) # check if the distribution is normal (norm) or not (anorm)

# parameter values
res$par
A<-as.numeric(res$par[1])
B<-as.numeric(res$par[2])


# Calculate P50 and P88
Kmax <- B
P88 <- ((Kmax*0.12)-Kmax)/A
P50 <- ((Kmax*0.5)-Kmax)/A

# Uncertainty around parameters
# calculate sd around each parameter using the hessian matrix
sterror<-sqrt(diag(solve(-1*res$hessian)))
Asd<- as.numeric(sterror[1])
Bsd<- as.numeric(sterror[2])

Alow<- A - Asd
Aup<- A + Asd
Blow<- B - Bsd
Bup<- B + Bsd


# obtain the VC curve and the uncertainty around it
## linear function = A*(x)+B
myfun <- function(x) A*(x)+B # mean curve
myfun_low1 <- function(x) Alow*(x)+B # low A
myfun_low2 <- function(x) A*(x)+Blow # low B
myfun_up1 <- function(x) Aup*(x)+B # up A
myfun_up2 <- function(x) A*(x)+Bup # up B


# plot VC curve using ggplot
p1<-ggplot(dt_spp, aes(x=Pf, y=Kleaf_area)) +
  geom_point(size=4, shape=1, alpha = .8, color = "black", stroke = 1)+
  stat_function(fun = myfun_low1, color = "grey", size = 1.5)+
  stat_function(fun = myfun_low2, color = "grey", size = 1.5)+
  stat_function(fun = myfun_up1, color = "grey", size = 1.5)+
  stat_function(fun = myfun_up2, color = "grey", size = 1.5)+
  stat_function(fun = myfun, color = "black", size = 1)+
  labs(title = spp_target, y= "Kleaf (mmol m-2 s-1 MPa-1)", x= "Leaf water potential (-MPa)")+
  theme_classic()+
  theme(
    axis.title.x = element_text(size=14),
    axis.title.y = element_text(size=14),
    axis.text.x = element_text(size=14, color = "black"),
    axis.text.y = element_text(size=14, color = "black"),
    axis.line = element_line(size = 1, linetype = "solid")
  )+geom_vline(xintercept= P50, linetype="solid", color = "orange", lwd = 1)+
  geom_vline(xintercept= P88, linetype="solid", color = "red", lwd = 1);p1

#save plot
#ggsave(paste0(spp_target,"_P50_linear.png"), width = 10, height = 10, dpi = 300, units = "cm", device='png')



