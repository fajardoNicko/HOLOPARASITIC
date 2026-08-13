#####################################################
#        CALCULATE MECHANICAL TRAITS                #
#####################################################

# LOAD PACKAGES -------------------------------------
library(ggpubr);library(gdata)
library(lubridate);library(mgcv); library(ggarrange);
library(ggmap); library(tidyverse); library(stringr)

# IMPORT DATA ---------------------------------------

spp<-"Bar_pur" # TYPE THE SPECIES NAME HERE!!!!

# read in files - MATLAB outputs

file_name <- unlist(list.files(path=paste0("DataS1/venation_function/force_displacement_curves/", spp)))

file_name

# check if all excel files in results folder are listed here 
length(file_name) 

# PUNCHING TESTS --------------------------------------

# selecting the force and displacement data from punch tests
P<- str_subset(file_name, "_P")
P
punch<-list()
for (i in 1:length(P)){
  punch[[i]] <- data.frame(read.csv(paste0("DataS1/venation_function/force_displacement_curves/", spp, "/",P[i]))[-c(1,2,3,4),])%>%
    tidyr::separate(., col = 1, into = c("Reading", "Load", "Time"), sep ="\t")
    punch[[i]]<-punch[[i]]%>%mutate(punch[[i]],Reading = as.numeric(punch[[i]]$Reading), Load = as.numeric(punch[[i]]$Load), Time = as.numeric(punch[[i]]$Time))
}

# replicate 1
Dist1 <- punch[[5]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force1 <- punch[[1]]%>% mutate(Force = abs(Load []))%>% add_column (rep = 1)%>%
  dplyr::select("Time", "Force", "rep")
# replicate 2
Dist2 <- punch[[6]] %>% mutate(Dist = abs(Load []))%>%
  dplyr::select("Time", "Dist")
Force2 <- punch[[2]]%>% mutate(Force = abs(Load []))%>% add_column (rep = 2)%>%
  dplyr::select("Time", "Force", "rep")
#replicate 3
Dist3 <- punch[[7]] %>% mutate(Dist = abs(Load []))%>%
  dplyr::select("Time", "Dist")
Force3 <- punch[[3]]%>% mutate(Force = abs(Load []))%>% add_column (rep = 3)%>%
  dplyr::select("Time", "Force", "rep")
#replicate 4
Dist4 <- punch[[8]] %>% mutate(Dist = abs(Load []))%>%
  dplyr::select("Time", "Dist")
Force4 <- punch[[4]]%>% mutate(Force = abs(Load []))%>% add_column (rep = 3)%>%
  dplyr::select("Time", "Force", "rep")

# importing supplementary data
sup_punch<-  read_csv("DataS1/venation_function/UCBG_venation_mechanics.csv") %>% 
            filter(spp_code == spp)%>% #filtering data only for the target spp
            add_column(f_max = NA, dis = NA) # adding columns to be filled with maximum force (f_max) and displacement (dis) data

# interpolating distances using GAMs
m_dist1 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist1)
Force1$pred_dist<-as.vector(predict(m_dist1, newdata=Force1))
glimpse(Force1)
plot(pred_dist ~ Time, data = Force1)
plot(Force ~ pred_dist, data = Force1)

m_dist2 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist2)
Force2$pred_dist<-as.vector(predict(m_dist2, newdata=Force2))
plot(pred_dist ~ Time, data = Force2)
plot(Force ~ pred_dist, data = Force2)

m_dist3 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist3)
Force3$pred_dist<-as.vector(predict(m_dist3, newdata=Force3))
plot(pred_dist ~ Time, data = Force3)
plot(Force ~ pred_dist, data = Force3)

m_dist4 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist4)
Force4$pred_dist<-as.vector(predict(m_dist4, newdata=Force4))
plot(pred_dist ~ Time, data = Force4)
plot(Force ~ pred_dist, data = Force4)

# saving the interpolated data

write.csv(rbind(Force1, Force2, Force3, Force4), file.path(paste0("DataS1/venation_function/force_displacement_curves/", spp), paste0("Punch_interpol_", spp, ".csv")), row.names=FALSE)
        

# plotting force x displacement curves

punch1<-ggplot(data=Force1, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Punch - Rep1"))+
  theme_bw();punch1


punch2<-ggplot(data=Force2, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Punch - Rep2"))+
  theme_bw();punch2

punch3<-ggplot(data=Force3, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Punch - Rep3"))+
  theme_bw();punch3

punch4<-ggplot(data=Force4, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Punch - Rep4"))+
  theme_bw();punch4

# saving plots
punch_plot<-ggarrange(punch1, punch2, punch3,punch4, ncol =2, nrow=2)
punch_plot

tiff(filename=paste0(spp,"_Punch_plot.tiff"),width=300,height =300,units="mm",pointsize = 12,bg="white",res=300)
punch_plot
dev.off()

# extracting maximum force and displacement data
X11()
punch1
MAX<-gglocator(n=1);MAX
sup_punch$f_max[1]<-MAX[2][[1]];sup_punch$f_max[1] # SELECT THE POINT OF MAXIMUM FORCE
points<-gglocator(2);points # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_punch$dis[1]<-points[[1]][2]-points[[1]][1];sup_punch$dis[1]

punch2
MAX2<-gglocator(n=1);MAX2
sup_punch$f_max[2]<-MAX2[2][[1]];sup_punch$f_max[2] # SELECT THE POINT OF MAXIMUM FORCE
points2<-gglocator(2);points2 # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_punch$dis[2]<-points2[[1]][2]-points2[[1]][1];sup_punch$dis[2]

punch3
MAX3<-gglocator(n=1);MAX3
sup_punch$f_max[3]<-MAX3[2][[1]];sup_punch$f_max[3] # SELECT THE POINT OF MAXIMUM FORCE
points3<-gglocator(2);points3 # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_punch$dis[3]<-points3[[1]][2]-points3[[1]][1];sup_punch$dis[3]

punch4
MAX4<-gglocator(n=1);MAX4
sup_punch$f_max[4]<-MAX4[2][[1]];sup_punch$f_max[4] # SELECT THE POINT OF MAXIMUM FORCE
points4<-gglocator(2);points4 # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_punch$dis[4]<-points4[[1]][2]-points4[[1]][1];sup_punch$dis[4]
dev.off()

# calculating mechanical properties
A_m2<-0.00009498 # cross-sectional area of the punch rode
punch_results<-sup_punch%>%
  mutate(P_strength = (f_max/A_m2)/1000)%>% # Punch Strength in KN m-2
  mutate(P_spec_strength = (P_strength/(punch_thickness/1000))/1000)%>% # Specific punch strength in MN m-2 m-1
  mutate(P_work = (f_max/A_m2)*(dis/1000))%>% # Work to punch in J m-2
  mutate(P_spec_work = (P_work/(punch_thickness/1000))/1000) # Specific work to punch KJ m-2 m-1

# saving punch results
glimpse(punch_results)
write.csv(punch_results, file.path("DataS1/venation_function/force_displacement_curves/", paste0("Punch_results_", spp, ".csv")), row.names=FALSE)

# SHEARING TESTS ------------------------------------------------

# selecting the force and displacement data from shearing tests
S<- str_subset(file_name, "_S")
S

shear<-list()
for (i in 1:length(S)){
  shear[[i]] <- data.frame(read.csv(paste0("DataS1/venation_function/force_displacement_curves/", spp, "/",S[i]))[-c(1,2,3,4),])%>%
    tidyr::separate(., col = 1, into = c("Reading", "Load", "Time"), sep ="\t")
  shear[[i]]<-shear[[i]]%>%mutate(shear[[i]],Reading = as.numeric(shear[[i]]$Reading), Load = as.numeric(shear[[i]]$Load), Time = as.numeric(shear[[i]]$Time))
}
glimpse(shear[[1]])

# replicate 1
Dist1 <- shear[[4]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force1 <- shear[[1]]%>% mutate(Force = abs(Load))%>% add_column (rep = 1)%>%
  dplyr::select("Time", "Force", "rep")
# replicate 2
Dist2 <- shear[[5]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force2 <- shear[[2]]%>% mutate(Force = abs(Load))%>% add_column (rep = 2)%>%
  dplyr::select("Time", "Force", "rep")
#replicate 3
Dist3 <- shear[[6]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force3 <- shear[[3]]%>% mutate(Force = abs(Load))%>% add_column (rep = 3)%>%
  dplyr::select("Time", "Force", "rep")

# importing supplementar data
sup_shear<- read_csv("DataS1/venation_function/UCBG_venation_mechanics.csv") %>% 
  filter(spp_code == spp)%>% #filtering data only for the target spp
  add_column(f_maxM = NA, disM = NA, f_maxL = NA, disL = NA) # adding columns to be filled with maximum force (f_max) and displacement (dis) data
glimpse(sup_shear)

# interpolating distances using GAMs
m_dist1 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist1)
Force1$pred_dist<-as.vector(predict(m_dist1, newdata=Force1))
plot(pred_dist ~ Time, data = Force1)
plot(Force ~ pred_dist, data = Force1)

m_dist2 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist2)
Force2$pred_dist<-as.vector(predict(m_dist2, newdata=Force2))
plot(pred_dist ~ Time, data = Force2)
plot(Force ~ pred_dist, data = Force2)

m_dist3 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist3)
Force3$pred_dist<-as.vector(predict(m_dist3, newdata=Force3))
plot(pred_dist ~ Time, data = Force3)
plot(Force ~ pred_dist, data = Force3)

# saving the interpolated data

write.csv(rbind(Force1, Force2, Force3), file.path(paste0("DataS1/venation_function/force_displacement_curves/", spp), paste0("Shear_interpol_", spp, ".csv")), row.names=FALSE)


# plotting force x displacement curves

shear1<-ggplot(data=Force1, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Shear - Rep1"))+
  theme_bw();shear1

shear2<-ggplot(data=Force2, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Shear - Rep2"))+
  theme_bw();shear2

shear3<-ggplot(data=Force3, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Shear - Rep3"))+
  theme_bw();shear3

# saving plots
shear_plot<-ggarrange(shear1, shear2, shear3, ncol =2, nrow=2)
shear_plot

tiff(filename=paste0(spp,"_Shear_plot.tiff"),width=300,height =300,units="mm",pointsize = 12,bg="white",res=300)
shear_plot
dev.off()

# extracting maximum force and displacement data
X11()
shear1
MAX_M<-gglocator(n=1);MAX_M # SELECT THE POINT OF MAXIMUM FORCE FOR THE MIDRIB
sup_shear$f_maxM[1]<-MAX_M[2][[1]];sup_shear$f_maxM[1] 
pointsM<-gglocator(2);pointsM # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_shear$disM[1]<-pointsM[[1]][2]-pointsM[[1]][1];sup_shear$disM[1]
MAX_L<-gglocator(n=1);MAX_L # SELECT THE POINT OF MAXIMUM FORCE FOR THE LAMINA
sup_shear$f_maxL[1]<-MAX_L[2][[1]];sup_shear$f_maxL[1] 
pointsL<-gglocator(2);pointsL # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_shear$disL[1]<-pointsL[[1]][2]-pointsL[[1]][1];sup_shear$disL[1]

shear2
MAX_M<-gglocator(n=1);MAX_M # SELECT THE POINT OF MAXIMUM FORCE FOR THE MIDRIB
sup_shear$f_maxM[2]<-MAX_M[2][[1]];sup_shear$f_maxM[2] 
pointsM<-gglocator(2);pointsM # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_shear$disM[2]<-pointsM[[1]][2]-pointsM[[1]][1];sup_shear$disM[2]
MAX_L<-gglocator(n=1);MAX_L # SELECT THE POINT OF MAXIMUM FORCE FOR THE LAMINA
sup_shear$f_maxL[2]<-MAX_L[2][[1]];sup_shear$f_maxL[2] 
pointsL<-gglocator(2);pointsL # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_shear$disL[2]<-pointsL[[1]][2]-pointsL[[1]][1];sup_shear$disL[2]

shear3
MAX_M<-gglocator(n=1);MAX_M # SELECT THE POINT OF MAXIMUM FORCE FOR THE MIDRIB
sup_shear$f_maxM[3]<-MAX_M[2][[1]];sup_shear$f_maxM[3] 
pointsM<-gglocator(2);pointsM # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_shear$disM[3]<-pointsM[[1]][2]-pointsM[[1]][1];sup_shear$disM[3]
MAX_L<-gglocator(n=1);MAX_L # SELECT THE POINT OF MAXIMUM FORCE FOR THE LAMINA
sup_shear$f_maxL[3]<-MAX_L[2][[1]];sup_shear$f_maxL[3] 
pointsL<-gglocator(2);pointsL # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_shear$disL[3]<-pointsL[[1]][2]-pointsL[[1]][1];sup_shear$disL[3]

dev.off()

# calculating mechanical properties
glimpse(sup_shear)
shear_results<-sup_shear%>%
  mutate(CM = (shear_thickness_midrib/1000) * (shear_width_midrib/1000), CL = (shear_thickness_lamina/1000) * (shear_width_lamina/1000))%>% # cross-sectional area of shear
  mutate(S_strength_M = (f_maxM/(CM))/1000000, S_strength_L = (f_maxL/(CL))/1000000)%>% # Shear Strength in MN m-2
  mutate(S_work_M = (f_maxM/(disM/1000))*(shear_width_midrib/1000), S_work_L = (f_maxL/(disL/1000))*(shear_width_lamina/1000))%>% # Work to shear in J m-1
  mutate(S_spec_work_M = (S_work_M/(shear_thickness_midrib/1000))/1000, S_spec_work_L = (S_work_L/(shear_thickness_lamina/1000))/1000) # Specific work to shear KJ m-2 

# saving shearing results
glimpse(shear_results)
write.csv(shear_results, file.path("DataS1/venation_function/force_displacement_curves/", paste0("Shear_results_", spp, ".csv")), row.names=FALSE)

# SHEARING TESTS FOR FERNS ------------------------------------------------

# selecting the force and displacement data from shearing tests
S<- str_subset(file_name, "_S")

shear<-list()
for (i in 1:length(S)){
  shear[[i]] <- data.frame(read.csv(paste0("DataS1/venation_function/force_displacement_curves/", spp, "/",S[i]))[-c(1,2,3,4),])%>%
    tidyr::separate(., col = 1, into = c("Reading", "Load", "Time"), sep ="\t")
  shear[[i]]<-shear[[i]]%>%mutate(shear[[i]],Reading = as.numeric(shear[[i]]$Reading), Load = as.numeric(shear[[i]]$Load), Time = as.numeric(shear[[i]]$Time))
}
glimpse(shear[[1]])

# replicate 1 lamina
S
Dist1 <- shear[[7]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force1 <- shear[[1]]%>% mutate(Force = abs(Load))%>% add_column (rep = 1)%>%
  dplyr::select("Time", "Force", "rep")

# replicate 2 lamina
S
Dist2 <- shear[[8]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force2 <- shear[[2]]%>% mutate(Force = abs(Load))%>% add_column (rep = 2)%>%
  dplyr::select("Time", "Force", "rep")

#replicate 3 lamina
S
Dist3 <- shear[[9]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force3 <- shear[[3]]%>% mutate(Force = abs(Load))%>% add_column (rep = 3)%>%
  dplyr::select("Time", "Force", "rep")

# replicate 1 midrib
S
Dist4 <- shear[[10]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force4 <- shear[[4]]%>% mutate(Force = abs(Load))%>% add_column (rep = 1)%>%
  dplyr::select("Time", "Force", "rep")

# replicate 2 midrib
S
Dist5 <- shear[[11]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force5 <- shear[[5]]%>% mutate(Force = abs(Load))%>% add_column (rep = 2)%>%
  dplyr::select("Time", "Force", "rep")

# replicate 3 midrib
S
Dist6 <- shear[[12]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force6 <- shear[[6]]%>% mutate(Force = abs(Load))%>% add_column (rep = 3)%>%
  dplyr::select("Time", "Force", "rep")

# importing supplementar data
sup_shear<-  read_csv("DataS1/venation_function/UCBG_venation_mechanics.csv") %>% 
  filter(spp_code == spp)%>% #filtering data only for the target spp
  add_column(f_maxM = NA, disM = NA, f_maxL = NA, disL = NA) # adding columns to be filled with maximum force (f_max) and displacement (dis) data
glimpse(sup_shear)

# interpolating distances using GAMs
m_dist1 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist1)
Force1$pred_dist<-as.vector(predict(m_dist1, newdata=Force1))

m_dist2 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist2)
Force2$pred_dist<-as.vector(predict(m_dist2, newdata=Force2))

m_dist3 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist3)
Force3$pred_dist<-as.vector(predict(m_dist3, newdata=Force3))

m_dist4 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist4)
Force4$pred_dist<-as.vector(predict(m_dist4, newdata=Force4))

m_dist5 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist5)
Force5$pred_dist<-as.vector(predict(m_dist5, newdata=Force5))

m_dist6 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist6)
Force6$pred_dist<-as.vector(predict(m_dist6, newdata=Force6))

# saving the interpolated data

write.csv(rbind(Force1, Force2, Force3, Force4, Force5, Force6), file.path(paste0("DataS1/venation_function/force_displacement_curves/", spp), paste0("Shear_interpol_", spp, ".csv")), row.names=FALSE)


# plotting force x displacement curves

shear1<-ggplot(data=Force1, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Shear midrib - Rep1"))+
  theme_bw();shear1

shear2<-ggplot(data=Force2, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Shear midrib- Rep2"))+
  theme_bw();shear2

shear3<-ggplot(data=Force3, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Shear midrib- Rep3"))+
  theme_bw();shear3

shear4<-ggplot(data=Force4, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Shear lamina- Rep1"))+
  theme_bw();shear4

shear5<-ggplot(data=Force5, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Shear lamina- Rep2"))+
  theme_bw();shear5

shear6<-ggplot(data=Force6, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Shear lamina- Rep3"))+
  theme_bw();shear6
# saving plots
shear_plot<-ggarrange(shear1, shear2, shear3, shear4, shear5, shear6, ncol =2, nrow=3)
shear_plot

tiff(filename=paste0(spp,"_Shear_plot.tiff"),width=300,height =300,units="mm",pointsize = 12,bg="white",res=300)
shear_plot
dev.off()

# extracting maximum force and displacement data
X11()
shear1
MAX_M<-gglocator(n=1);MAX_M # SELECT THE POINT OF MAXIMUM FORCE FOR THE MIDRIB
sup_shear$f_maxM[1]<-MAX_M[2][[1]];sup_shear$f_maxM[1] 
pointsM<-gglocator(2);pointsM # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_shear$disM[1]<-pointsM[[1]][2]-pointsM[[1]][1];sup_shear$disM[1]

shear4
MAX_L<-gglocator(n=1);MAX_L # SELECT THE POINT OF MAXIMUM FORCE FOR THE LAMINA
sup_shear$f_maxL[1]<-MAX_L[2][[1]];sup_shear$f_maxL[1] 
pointsL<-gglocator(2);pointsL # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_shear$disL[1]<-pointsL[[1]][2]-pointsL[[1]][1];sup_shear$disL[1]

shear2
MAX_M<-gglocator(n=1);MAX_M # SELECT THE POINT OF MAXIMUM FORCE FOR THE MIDRIB
sup_shear$f_maxM[2]<-MAX_M[2][[1]];sup_shear$f_maxM[2] 
pointsM<-gglocator(2);pointsM # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_shear$disM[2]<-pointsM[[1]][2]-pointsM[[1]][1];sup_shear$disM[2]

shear5
MAX_L<-gglocator(n=1);MAX_L # SELECT THE POINT OF MAXIMUM FORCE FOR THE LAMINA
sup_shear$f_maxL[2]<-MAX_L[2][[1]];sup_shear$f_maxL[2] 
pointsL<-gglocator(2);pointsL # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_shear$disL[2]<-pointsL[[1]][2]-pointsL[[1]][1];sup_shear$disL[2]

shear3
MAX_M<-gglocator(n=1);MAX_M # SELECT THE POINT OF MAXIMUM FORCE FOR THE MIDRIB
sup_shear$f_maxM[3]<-MAX_M[2][[1]];sup_shear$f_maxM[3] 
pointsM<-gglocator(2);pointsM # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_shear$disM[3]<-pointsM[[1]][2]-pointsM[[1]][1];sup_shear$disM[3]

shear6
MAX_L<-gglocator(n=1);MAX_L # SELECT THE POINT OF MAXIMUM FORCE FOR THE LAMINA
sup_shear$f_maxL[3]<-MAX_L[2][[1]];sup_shear$f_maxL[3] 
pointsL<-gglocator(2);pointsL # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_shear$disL[3]<-pointsL[[1]][2]-pointsL[[1]][1];sup_shear$disL[3]

dev.off()

# calculating mechanical properties
glimpse(sup_shear)
shear_results<-sup_shear%>%
  mutate(CM = (S_LthM/1000) * (S_WM/1000), CL = (S_LthL/1000) * (S_WL/1000))%>% # cross-sectional area of shear
  mutate(S_strength_M = (f_maxM/(CM))/1000000, S_strength_L = (f_maxL/(CL))/1000000)%>% # Shear Strength in MN m-2
 # mutate(spec_strength = (strength/(Lth_mm/1000))/1000)%>% # Specific shear strength in MN m-2 m-1
  mutate(S_work_M = (f_maxM/(disM/1000))*(S_WM/1000), S_work_L = (f_maxL/(disL/1000))*(S_WL/1000))%>% # Work to shear in J m-1
  mutate(S_spec_work_M = (S_work_M/(S_LthM/1000))/1000, S_spec_work_L = (S_work_L/(S_LthL/1000))/1000) # Specific work to shear KJ m-2 

# saving shearing results
glimpse(shear_results)
write.csv(shear_results, file.path("DataS1/venation_function/force_displacement_curves/", paste0("Shear_results_", spp, ".csv")), row.names=FALSE)

# BENDING TESTS --------------------------------------------

# selecting the force and displacement data from bending tests

B<- str_subset(file_name, "_B")
B
bend<-list()
for (i in 1:length(B)){
  bend[[i]] <- data.frame(read.csv(paste0("DataS1/venation_function/force_displacement_curves/", spp, "/",B[i]))[-c(1,2,3,4),])%>%
    tidyr::separate(., col = 1, into = c("Reading", "Load", "Time"), sep ="\t")
  bend[[i]]<-bend[[i]]%>%mutate(bend[[i]],Reading = as.numeric(bend[[i]]$Reading), Load = as.numeric(bend[[i]]$Load), Time = as.numeric(bend[[i]]$Time))
}

# IF YOU HAVE ONLY WHOLE LEAF BENDING DATA

# replicate 1
Dist1_W <- bend[[4]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force1_W <- bend[[1]]%>% mutate(Force = abs(Load))%>% add_column (rep = 1)%>%
  dplyr::select("Time", "Force", "rep")

# replicate 2
Dist2_W <- bend[[5]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force2_W <- bend[[2]]%>% mutate(Force = abs(Load))%>% add_column (rep = 2)%>%
  dplyr::select("Time", "Force", "rep")


#replicate 3
Dist3_W <- bend[[6]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force3_W <- bend[[3]]%>% mutate(Force = abs(Load))%>% add_column (rep = 3)%>%
  dplyr::select("Time", "Force", "rep")


# IF YOU HAVE BOTH LAMINA AND WHOLE LEAF BENDING DATA
# replicate 1
Dist1_L <- bend[[7]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force1_L <- bend[[1]]%>% mutate(Force = abs(Load))%>% add_column (rep = 1)%>%
  dplyr::select("Time", "Force", "rep")
Dist1_W <- bend[[10]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force1_W <- bend[[4]]%>% mutate(Force = abs(Load))%>% add_column (rep = 1)%>%
  dplyr::select("Time", "Force", "rep")

# replicate 2
Dist2_L <- bend[[8]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force2_L <- bend[[2]]%>% mutate(Force = abs(Load))%>% add_column (rep = 2)%>%
  dplyr::select("Time", "Force", "rep")
Dist2_W <- bend[[11]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force2_W <- bend[[5]]%>% mutate(Force = abs(Load))%>% add_column (rep = 2)%>%
  dplyr::select("Time", "Force", "rep")


#replicate 3
Dist3_L <- bend[[9]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force3_L <- bend[[3]]%>% mutate(Force = abs(Load))%>% add_column (rep = 3)%>%
  dplyr::select("Time", "Force", "rep")
Dist3_W <- bend[[12]] %>% mutate(Dist = abs(Load))%>%
  dplyr::select("Time", "Dist")
Force3_W <- bend[[6]]%>% mutate(Force = abs(Load))%>% add_column (rep = 3)%>%
  dplyr::select("Time", "Force", "rep")

# importing supplementar data
sup_bend<-  read_csv("DataS1/venation_function/UCBG_venation_mechanics.csv") %>% 
  filter(spp_code == spp)%>% #filtering data only for the target spp
  add_column(f_maxW = NA, disW = NA, f_maxL = NA, disL = NA) # adding columns to be filled with maximum force (f_max) and displacement (dis) data
sup_bend$bending_span_lamina<-as.numeric(sup_bend$bending_span_lamina)
sup_bend$bending_thickness_lamina<-as.numeric(sup_bend$bending_thickness_lamina)
sup_bend$bending_width_lamina<-as.numeric(sup_bend$bending_width_lamina)

glimpse(sup_bend)

# interpolating distances using GAMs
m_dist1 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist1_L)
Force1_L$pred_dist<-as.vector(predict(m_dist1, newdata=Force1_L))
m_dist1 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist1_W)
Force1_W$pred_dist<-as.vector(predict(m_dist1, newdata=Force1_W))

m_dist2 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist2_L)
Force2_L$pred_dist<-as.vector(predict(m_dist2, newdata=Force2_L))
m_dist2 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist2_W)
Force2_W$pred_dist<-as.vector(predict(m_dist2, newdata=Force2_W))

m_dist3 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist3_L)
Force3_L$pred_dist<-as.vector(predict(m_dist3, newdata=Force3_L))
m_dist3 <- gam(abs(Dist)~s(Time,bs='cs'), data=Dist3_W)
Force3_W$pred_dist<-as.vector(predict(m_dist3, newdata=Force3_W))

# saving the interpolated data

#IF YOU HAVE ONLY WHOLE LEAF BENDING DATA
write.csv(rbind(Force1_W, Force2_W, Force3_W), 
          file.path(paste0("DataS1/venation_function/force_displacement_curves/", spp), paste0("Bend_interpol_", spp, ".csv")), 
          row.names=FALSE)

#IF YOU HAVE BOTH LAMINA AND WHOLE LEAF BENDING DATA
write.csv(rbind(Force1_L, Force1_W, Force2_L, Force2_W, Force3_L, Force3_W), 
          file.path(paste0("DataS1/venation_function/force_displacement_curves/", spp), paste0("Bend_interpol_", spp, ".csv")), 
          row.names=FALSE)

# plotting force x displacement curves

bend1_L<-ggplot(data=Force1_L, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Bend Lamina - Rep1"))+
  theme_bw();bend1_L
bend1_W<-ggplot(data=Force1_W, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Bend Whole leaf - Rep1"))+
  theme_bw();bend1_W

bend2_L<-ggplot(data=Force2_L, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Bend Lamina - Rep2"))+
  theme_bw();bend2_L
bend2_W<-ggplot(data=Force2_W, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Bend Whole leaf - Rep2"))+
  theme_bw();bend2_W

bend3_L<-ggplot(data=Force3_L, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Bend Lamina - Rep3"))+
  theme_bw();bend3_L
bend3_W<-ggplot(data=Force3_W, aes(abs(pred_dist), abs(Force)))+
  geom_line(show.legend = FALSE, size = 0.5, col = "black")+
  labs(y="Force (N)", x = "Displacement (mm)", title = paste(spp,"Bend Whole leaf - Rep3"))+
  theme_bw();bend3_W

# saving plots
# IF YOU HAVE ONLY WHOLE LEAF BENDING DATA 
bend_plot<-ggarrange(bend1_W,  bend2_W,  bend3_W, ncol =2, nrow=2)
bend_plot
#IF YOU HAVE BOTH LAMINA AND WHOLE LEAF BENDING DATA
bend_plot<-ggarrange(bend1_L, bend1_W, bend2_L, bend2_W, bend3_L, bend3_W, ncol =2, nrow=3)
bend_plot


tiff(filename=paste0(spp,"_Bend_plot.tiff"),width=300,height =300,units="mm",pointsize = 12,bg="white",res=300)
bend_plot
dev.off()

# extracting maximum force and displacement data

X11()
bend1_L
MAX_L<-gglocator(n=1);MAX_L # SELECT THE POINT OF MAXIMUM FORCE FOR THE LAMINA
sup_bend$f_maxL[1]<-MAX_L[2][[1]];sup_bend$f_maxL[1] 
pointsL<-gglocator(2);pointsL # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_bend$disL[1]<-pointsL[[1]][2]-pointsL[[1]][1];sup_bend$disL[1]

bend1_W
MAX_W<-gglocator(n=1);MAX_W # SELECT THE POINT OF MAXIMUM FORCE FOR THE WHOLE-LEAF
sup_bend$f_maxW[1]<-MAX_W[2][[1]];sup_bend$f_maxW[1] 
pointsW<-gglocator(2);pointsW # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_bend$disW[1]<-pointsW[[1]][2]-pointsW[[1]][1];sup_bend$disW[1]

bend2_L
MAX_L<-gglocator(n=1);MAX_L # SELECT THE POINT OF MAXIMUM FORCE FOR THE LAMINA
sup_bend$f_maxL[2]<-MAX_L[2][[1]];sup_bend$f_maxL[2] 
pointsL<-gglocator(2);pointsL # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_bend$disL[2]<-pointsL[[1]][2]-pointsL[[1]][1];sup_bend$disL[2]

bend2_W
MAX_W<-gglocator(n=1);MAX_W # SELECT THE POINT OF MAXIMUM FORCE FOR THE WHOLE-LEAF
sup_bend$f_maxW[2]<-MAX_W[2][[1]];sup_bend$f_maxW[2] 
pointsW<-gglocator(2);pointsW # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_bend$disW[2]<-pointsW[[1]][2]-pointsW[[1]][1];sup_bend$disW[2]

bend3_L
MAX_L<-gglocator(n=1);MAX_L # SELECT THE POINT OF MAXIMUM FORCE FOR THE LAMINA
sup_bend$f_maxL[3]<-MAX_L[2][[1]];sup_bend$f_maxL[3] 
pointsL<-gglocator(2);pointsL # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!)
sup_bend$disL[3]<-pointsL[[1]][2]-pointsL[[1]][1];sup_bend$disL[3]

bend3_W
MAX_W<-gglocator(n=1);MAX_W # SELECT THE POINT OF MAXIMUM FORCE FOR THE WHOLE-LEAF
sup_bend$f_maxW[3]<-MAX_W[2][[1]];sup_bend$f_maxW[3] 
pointsW<-gglocator(2);pointsW # SELECT THE DISPLACEMENT POINTS (FIRST THE SMALL VALUE!!
sup_bend$disW[3]<-pointsW[[1]][2]-pointsW[[1]][1];sup_bend$disW[3]

dev.off()

# calculating mechanical properties
glimpse(sup_bend)
bend_results<-sup_bend%>%
  mutate (IW =((bending_width_whole/1000)*((bending_thickness_whole/1000)^3))/12, IL = ((bending_width_lamina/1000)*((bending_thickness_lamina/1000)^3))/12)%>% # second moment of area
  mutate (FEW = ((f_maxW/(disW/1000))*((bending_span_whole/100)^3)/(48*IW))/1000000, FEL = ((f_maxL/(disL/1000))*((bending_span_lamina/100)^3)/(48*IL))/1000000)%>% # flexural modulus of elasticity in MN m-2
  mutate (FSW =(((f_maxW/(disW/1000))*((bending_span_whole/100)^3)/(48*(bending_width_whole/1000))))*1000, 
          FSL =(((f_maxL/(disL/1000))*((bending_span_lamina/100)^3)/(48*(bending_width_lamina/1000))))*1000) # Flexural stiffness mN m-2 m-1

# saving bending results
glimpse(bend_results)
write.csv(bend_results, file.path("DataS1/venation_function/force_displacement_curves", paste0("Bend_results_", spp, ".csv")), row.names=FALSE)


#END
# CLEAR THE WORKSPACE BEFORE STARTING A NEW SPECIES!!