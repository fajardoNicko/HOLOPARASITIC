
######## R-script for calculating Kmax using the EFM method ####################################

# STEP 1 -  SETING DIRECTORY AND LOADING PACKAGES ######
library(tidyverse)
library(lubridate)
library(ggpubr)

# STEP 2 -  IMPORTING DATA ----------------

dat<-  read_csv("DataS1/venation_function/hydraulics/UCBG_venation_kmax.csv") 
glimpse(dat)


## STEP 3 - CALCULATING KLEAF -------------------------------------------

Kleaf_data_final<- dat%>% 
  mutate (Rtube_cor = 10^((1.3272*(20-TempW)-0.001053*(TempW-20)^2)/(TempW+105))*(1.002/0.8904)*Rtubes)%>% # Temperature correction for Rtube
  mutate (Pleaf = as.numeric(Pf) -0) %>% # calculate Pleaf
  mutate (Kleaf = (Ptube/Pleaf)* (1/Rtube_cor))%>% # calulate Kleaf
  mutate (Rleaf = 1/Kleaf) %>% # calculate Rleaf
  mutate (Kleaftcor = Kleaf/ (0.88862* (1/(10^((1.3272*(20-TempL)-0.001053*(TempL-20)^2)/(TempL+105))))))%>% # temperature correction for Kleaf
  mutate (Kleaf_area = Kleaftcor/(leaf_area/10000)) # normalizing Kleaf per leaf area in m2

glimpse(Kleaf_data_final) # checking final Kleaf values 

Kleaf_mean<- Kleaf_data_final%>% 
  filter(!is.na(Kleaf_area))%>%
  summarise(Kleaf_max = max (Kleaf_area), # calculating Kmax
            Kleaf_mean = mean(Kleaf_area), # calculating mean Kleaf
            Kleaf_sd = sd (Kleaf_area), # calculating sd for Kleaf
            n = n()) # number of replicates for Kleaf measurement