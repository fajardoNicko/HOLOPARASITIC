
######## R-script for calculating Dkleaf using the EFM method ####################################

# STEP 1 -  SETING DIRECTORY AND LOADING PACKAGES ######
library(tidyverse)
library(lubridate)
library(ggpubr)

# STEP 2 -  IMPORTING DATA ----------------

dat<-  read_csv("DataS1/venation_function/UCBG_venation_Dkleaf.csv") 
glimpse(dat)

fun<- read_csv("DataS1/venation_function/UCBG_venation_function.csv")
glimpse(fun)

## STEP 3 - CALCULATING KLEAF -------------------------------------------

dat<- dat%>% 
  mutate (Rtube_cor = 10^((1.3272*(20-TempW)-0.001053*(TempW-20)^2)/(TempW+105))*(1.002/0.8904)*Rtubes)%>% # Temperature correction for Rtube
  mutate (Pleaf = as.numeric(Pf) -0) %>% # calculate Pleaf
  mutate (Kleaf = (Ptube/Pleaf)* (1/Rtube_cor))%>% # calulate Kleaf
  mutate (Rleaf = 1/Kleaf) %>% # calculate Rleaf
  mutate (Kleaftcor = Kleaf/ (0.88862* (1/(10^((1.3272*(20-TempL)-0.001053*(TempL-20)^2)/(TempL+105))))))%>% # temperature correction for Kleaf
  mutate (Kleaf_area = Kleaftcor/(leaf_area/10000)) # normalizing Kleaf per leaf area in m2

glimpse(dat) # checking final Kleaf values 

## STEP 4 - CALCULATING KLEAF PERCENTUAL CHANGE -------------------------------------------

spp_code<- fun$spp_code
Dkleaf_final <- list()
for (i in 1:length(spp_code)) {
  Dkleaf<-dat%>%separate(treat, sep = "", into = c("rep", "treat"))%>%
    filter(spp_code == spp_code[i])%>%
    group_by(treat)%>%
    summarise(meanK = mean(Kleaf_area, na.rm = TRUE), sdK = sd(Kleaf_area, na.rm = TRUE))
  
  Kmax<- fun%>% filter(spp_code == spp_code[i])%>% select(Kleaf_max)
  
  decline_midrib <- ((Dkleaf$meanK[3] *100)/Kmax)-100
  decline_lamina <- ((Dkleaf$meanK[2] *100)/Kmax)-100
  decline_control <- ((Dkleaf$meanK[1] *100)/Kmax)-100
  Dkleaf_final[[i]]<- as.data.frame(cbind(spp_code[1],decline_midrib, decline_lamina, decline_control)) 
  colnames(Dkleaf_final[[i]])[1] = "spp_code"
  colnames(Dkleaf_final[[i]])[2] = "decline_midrib"
  colnames(Dkleaf_final[[i]])[3] = "decline_lamina"
  colnames(Dkleaf_final[[i]])[4] = "decline_control"
}

Dkleaf_final
