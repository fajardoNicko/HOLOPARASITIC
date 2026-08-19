"""Build 'DISTRICT STF - BIBLIOGRAPHY.docx' — APA 7th, hanging indent.

De-duplicated from the supplied list (86 pasted -> 58 unique), corrected against
Crossref, and completed with every work cited in the paper that had no entry.

Italic segments are marked with *asterisks*.
"""

import re
import unicodedata
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_LINE_SPACING

ENTRIES = [
    # ---- supplied list, corrected -----------------------------------------
    "Agronomist, C., & Johnson, J. (2024). *Function of xylem and phloem in a corn plant*. Bayer Crop Science. https://www.cropscience.bayer.us/articles/channel/function-of-xylem-and-phloem-in-a-corn-plant",
    "Al-Ward, H., Tan, C. K., & Lim, W. H. (2022). Caching transient data in Information-Centric Internet-of-Things (IC-IoT) networks: A survey. *Journal of Network and Computer Applications, 206*, 103491. https://doi.org/10.1016/j.jnca.2022.103491",
    "Barry, L., Cabrera, J. C. B., Lucas, M., Lobet, G., Boursiac, Y., & Grondin, A. (2025). Role of xylem in root hydraulics: Functionality and implications for drought adaptation. *Quantitative Plant Biology, 6*, e42. https://doi.org/10.1017/qpb.2025.10026",
    "Bascos, E. M. A., Fernando, E. S., Duya, M. V., & Rodriguez, L. J. V. (2021). Beginnings of a plant parasite: Early development of *Rafflesia consueloae* inside its *Tetrastigma* host. *Planta, 254*(3), 61. https://doi.org/10.1007/s00425-021-03710-4",
    "Bittencourt, P., Pereira, L., & Oliveira, R. (2018). Pneumatic method to measure plant xylem embolism. *Bio-protocol, 8*(20), e3059. https://doi.org/10.21769/bioprotoc.3059",
    "Boehm, H. (1893). Capillarit\u00e4t und Saftsteigen. *Berichte der Deutschen Botanischen Gesellschaft, 11*, 203\u2013212.",
    "Bozkurt, T. O., & Kamoun, S. (2020). The plant\u2013pathogen haustorial interface at a glance. *Journal of Cell Science, 133*(5), jcs237958. https://doi.org/10.1242/jcs.237958",
    "Casades\u00fas, A., & Munn\u00e9-Bosch, S. (2021). Holoparasitic plant\u2013host interactions and their impact on Mediterranean ecosystems. *Plant Physiology, 185*(4), 1325\u20131338. https://doi.org/10.1093/plphys/kiab030",
    "Chen, Y., Wu, H., Cai, J., Guo, S., Gan, X., Liu, X., & Yang, J. (2025). Molecular translocation between parasitic plants and their hosts. *Frontiers in Plant Science, 16*, 1716304. https://doi.org/10.3389/fpls.2025.1716304",
    "Choat, B., Jansen, S., Brodribb, T. J., Cochard, H., Delzon, S., Bhaskar, R., Bucci, S. J., Feild, T. S., Gleason, S. M., Hacke, U. G., Jacobsen, A. L., Lens, F., Maherali, H., Mart\u00ednez-Vilalta, J., Mayr, S., Mencuccini, M., Mitchell, P. J., Nardini, A., Pittermann, J., \u2026 Zanne, A. E. (2012). Global convergence in the vulnerability of forests to drought. *Nature, 491*(7426), 752\u2013755. https://doi.org/10.1038/nature11688",
    "Dawson, T. E., & Ehleringer, J. R. (1993). Water sources of plants as determined from xylem-water isotopic composition. In J. R. Ehleringer, A. E. Hall, & G. D. Farquhar (Eds.), *Stable isotopes and plant carbon-water relations* (pp. 465\u2013496). Academic Press.",
    "Denny, M. (2011). Tree hydraulics: How sap rises. *European Journal of Physics, 33*(1), 43\u201353. https://doi.org/10.1088/0143-0807/33/1/003",
    "De Swaef, T., Pieters, O., Appeltans, S., Borra-Serrano, I., Coudron, W., Couvreur, V., Garr\u00e9, S., Lootens, P., Nicola\u00ef, B., Pols, L., Cast, C. S., \u0160alagovi\u010d, J., Van Haeverbeke, M., Stock, M., & Wyffels, F. (2022). On the pivotal role of water potential to model plant physiological processes. *In Silico Plants, 4*(1), diab038. https://doi.org/10.1093/insilicoplants/diab038",
    "Dixon, H. H. (1894). On the ascent of sap. *Annals of Botany, 8*(4), 468\u2013470.",
    "Dixon, H. H., & Joly, J. (1895). On the ascent of sap. *Philosophical Transactions of the Royal Society B: Biological Sciences, 186*, 563\u2013576.",
    "Elshakhs, Y. S., Deliparaschos, K. M., Charalambous, T., Oliva, G., & Zolotas, A. (2024). A comprehensive survey on Delaunay triangulation: Applications, algorithms, and implementations over CPUs, GPUs, and FPGAs. *IEEE Access, 12*, 12562\u201312585. https://doi.org/10.1109/ACCESS.2024.3354709",
    "Fern\u00e1ndez-Aparicio, M., Reboud, X., & Gibot-Leclerc, S. (2016). Broomrape weeds: Underground mechanisms of parasitism and associated strategies for their control: A review. *Frontiers in Plant Science, 7*, 135. https://doi.org/10.3389/fpls.2016.00135",
    "Gogoi, A., Baruah, N., Poudel, M., Gupta, R., Baruah, G., & Borah, B. K. (2021). Parasitic plants as vectors for pathogens. IntechOpen. https://doi.org/10.5772/intechopen.100187",
    "Golbeck, J. (2013). Network structure and measures. In *Analyzing the social web* (pp. 25\u201344). Elsevier. https://doi.org/10.1016/B978-0-12-405531-5.00003-1",
    "Gooch, J. W. (Ed.). (2007). Hagen\u2013Poiseuille equation. In *Encyclopedic dictionary of polymers* (p. 477). Springer. https://doi.org/10.1007/978-0-387-30160-0_5664",
    "Goyet, V., Wada, S., Cui, S., Wakatake, T., Shirasu, K., Montiel, G., Simier, P., & Yoshida, S. (2019). Haustorium inducing factors for parasitic Orobanchaceae. *Frontiers in Plant Science, 10*, 1056. https://doi.org/10.3389/fpls.2019.01056",
    "Hatt, S. A., Grace, O. M., Zuntini, A. R., Cameron, D. D., & Thorogood, C. J. (2025). Parasitic plants show striking convergence in host preference across angiosperm lineages. *Annals of Botany, 135*(6), 1135\u20131146. https://doi.org/10.1093/aob/mcae180",
    "Haworth, M., Killi, D., Materassi, A., Raschi, A., & Centritto, M. (2016). Impaired stomatal control is associated with reduced photosynthetic physiology in crop species grown at elevated [CO\u2082]. *Frontiers in Plant Science, 7*, 1568. https://doi.org/10.3389/fpls.2016.01568",
    "Hegenauer, V., K\u00f6rner, M., & Albert, M. (2017). Plants under stress by parasitic plants. *Current Opinion in Plant Biology, 38*, 34\u201341. https://doi.org/10.1016/j.pbi.2017.04.006",
    "Henry, A., Wehler, R., Grondin, A., Franke, R., & Quintana, M. (2016). Environmental and physiological effects on grouping of drought-tolerant and susceptible rice varieties related to rice (*Oryza sativa*) root hydraulics under drought. *Annals of Botany, 118*(4), 711\u2013724. https://doi.org/10.1093/aob/mcw068",
    "Kong, X., Shi, Y., Yu, S., Liu, J., & Xia, F. (2019). Academic social networks: Modeling, analysis, mining and applications. *Journal of Network and Computer Applications, 132*, 86\u2013103. https://doi.org/10.1016/j.jnca.2019.01.029",
    "Lambio, I. A. F., Alviola, M. S., Luca\u00f1as, C. C., Barrion-Dupo, A. L. A., Duran, C. F. D., Cammayo, M. F. K. M., Taray, K. J., Eusebio, O. L., & Lit, I. L., Jr. (2024). First cavernicolous record of the holoparasitic *Balanophora abbreviata* Blume (Balanophoraceae), from Tayabas, Quezon, Philippines. *Journal of Asia-Pacific Biodiversity, 17*(1), 208\u2013213. https://doi.org/10.1016/j.japb.2023.11.012",
    "Liu, H., Xiao, Z., & Shen, L. (2023). Simulation-based study of low-Reynolds-number flow around a ventilated cavity. *Journal of Fluid Mechanics, 966*, A6. https://doi.org/10.1017/jfm.2023.431",
    "Ma, J., Zhao, Z., Lin, S., & Xie, Y. M. (2021). Topology of leaf veins: Experimental observation and computational morphogenesis. *Journal of the Mechanical Behavior of Biomedical Materials, 123*, 104788. https://doi.org/10.1016/j.jmbbm.2021.104788",
    "Malabrigo, P. L., Jr., Tobias, A. B., Witono, J., Mursidawati, S., Susatya, A., Mat Yunoh, S.-M., Wicaksono, A., & Raihandhany, R. (2025). Most of the world\u2019s largest flowers (genus *Rafflesia*) are now on the brink of extinction. *Plants, People, Planet, 7*(2), 331\u2013346. https://doi.org/10.1002/ppp3.10431",
    "Mander, L., & Williams, H. T. P. (2024). The robustness of some Carboniferous fossil leaf venation networks to simulated damage. *Royal Society Open Science, 11*(5), 240086. https://doi.org/10.1098/rsos.240086",
    "Maqsood, A., & Khaliq, H. (2022). Interaction of plant parasitic nematode with Fusarium wilt: A disease complex. *Jammu Kashmir Journal of Agriculture, 2*(2), 33\u201344. https://doi.org/10.56810/jkjagri.002.02.0047",
    "Mateus, N. S., Steppe, K., & Tricker, P. (2026). Scaling the plant hydraulic system: From xylem networks to whole-plant integration. *Journal of Experimental Botany, 77*(4), 885\u2013889. https://doi.org/10.1093/jxb/eraf532",
    "McCulloh, K. A., Sperry, J. S., & Adler, F. R. (2004). Murray\u2019s law and the hydraulic vs mechanical functioning of wood. *Functional Ecology, 18*(6), 931\u2013938. https://doi.org/10.1111/j.0269-8463.2004.00913.x",
    "McCulloh, K. A., Sperry, J. S., Meinzer, F. C., Lachenbruch, B., & Atala, C. (2009). Murray\u2019s law, the \u201cYarrum\u201d optimum, and the hydraulic architecture of compound leaves. *New Phytologist, 184*(1), 234\u2013244. https://doi.org/10.1111/j.1469-8137.2009.02950.x",
    "Murray, C. D. (1926). The physiological principle of minimum work: I. The vascular system and the cost of blood volume. *Proceedings of the National Academy of Sciences, 12*(3), 207\u2013214. https://doi.org/10.1073/pnas.12.3.207",
    "Nabity, P. D., Barron-Gafford, G. A., & Whiteman, N. K. (2021). Intraspecific competition for host resources in a parasite. *Current Biology, 31*(6), 1344\u20131350.e3. https://doi.org/10.1016/j.cub.2021.01.034",
    "Obico, J. J. A., Lapuz, R. S. C., Barcelona, J. F., & Pelser, P. B. (2024). What explains the high island endemicity of Philippine *Rafflesia*? A species distribution modeling analysis of three threatened parasitic plant species and their hosts. *American Journal of Botany, 111*(1), e16267. https://doi.org/10.1002/ajb2.16267",
    "Ossa, C. G., Aros-Mualin, D., Mujica, M. I., & P\u00e9rez, F. (2021). The physiological effect of a holoparasite over a cactus along an environmental gradient. *Frontiers in Plant Science, 12*, 763446. https://doi.org/10.3389/fpls.2021.763446",
    "Pelser, P. B., Barcelona, J. F., & Nickrent, D. L. (Eds.). (2024). *Aeginetia indica* L. In *Co\u2019s digital flora of the Philippines*. https://www.philippineplants.org/Families/Orobanchaceae.html",
    "P\u00e9rez-de-Luque, A. (2013). Interaction between parasitic weeds and their hosts. In D. M. Joel, J. Gressel, & L. J. Musselman (Eds.), *Parasitic Orobanchaceae: Parasitic mechanisms and control strategies* (pp. 75\u201386). Springer. https://doi.org/10.1007/978-3-642-38146-1",
    "Prasad, A., & Roy, M. (2020). Bioimpedance analysis of vascular tissue and fluid flow in human and plant body: A review. *Biosystems Engineering, 197*, 170\u2013187. https://doi.org/10.1016/j.biosystemseng.2020.06.006",
    "Qaderi, M. M., Martel, A. B., & Dixon, S. L. (2019). Environmental factors influence plant vascular system and water regulation. *Plants, 8*(3), 65. https://doi.org/10.3390/plants8030065",
    "Saleem, M., Zhang, J., Qasim, M., Iqbal, R., & Song, L. (2024). The correlation between nutrition and transport mechanism under abiotic stress in plants: A comprehensive review. *Phyton, 93*(6), 1325\u20131344. https://doi.org/10.32604/phyton.2024.048493",
    "Sarun, H. (2026). *Nematode and parasitic plant diseases*. Zenodo. https://doi.org/10.5281/zenodo.19394604",
    "Sharma, B. P., Sharma, A., Creado, R., Mety, S. S., Hossain, E., Jena, N., & Chand, G. (2025). *A note on Aeginetia indica L.: A holoparasitic plant of India*. Zenodo. https://doi.org/10.5281/zenodo.18104763",
    "Sullivan, J. (2021, December 4). *Unwanted guests: The weird world of parasitic plants*. Natural History Museum. https://www.nhm.ac.uk/discover/parasitic-plants.html",
    "Twyford, A. D. (2018). Parasitic plants. *Current Biology, 28*(16), R857\u2013R859. https://doi.org/10.1016/j.cub.2018.06.030",
    "Voegele, R. T., & Mendgen, K. (2003). Rust haustoria: Nutrient uptake and beyond. *New Phytologist, 159*(1), 93\u2013100. https://doi.org/10.1046/j.1469-8137.2003.00761.x",
    "Wason, J., Bouda, M., Lee, E. F., McElrone, A. J., Phillips, R. J., Shackel, K. A., Matthews, M. A., & Brodersen, C. R. (2021). Xylem network connectivity and embolism spread in grapevine (*Vitis vinifera* L.). *Plant Physiology, 186*(1), 373\u2013387. https://doi.org/10.1093/plphys/kiab045",
    "Westwood, J. H., Yoder, J. I., Timko, M. P., & dePamphilis, C. W. (2010). The evolution of parasitism in plants. *Trends in Plant Science, 15*(4), 227\u2013235. https://doi.org/10.1016/j.tplants.2010.01.004",
    "Wisniewski, S. J., & Brannan, G. D. (2024). *Correlation (coefficient, partial, and Spearman rank) and regression analysis*. StatPearls Publishing. https://www.ncbi.nlm.nih.gov/books/NBK606101/",
    "Wolitzky, A. (2022). *Graph theory and social networks* [Lecture slides]. MIT OpenCourseWare. https://ocw.mit.edu/courses/14-15-networks-spring-2022/mit14_15s22_lec2.pdf",
    "Zagorchev, L., St\u00f6ggl, W., Teofanova, D., Li, J., & Kranner, I. (2021). Plant parasites under pressure: Effects of abiotic stress on the interactions between parasitic plants and their hosts. *International Journal of Molecular Sciences, 22*(14), 7418. https://doi.org/10.3390/ijms22147418",
    "Zhang, J. X., & Hoshino, K. (2013). Microfluidics and micro total analytical systems. In *Molecular sensors and nanodevices* (pp. 103\u2013168). Elsevier. https://doi.org/10.1016/B978-1-4557-7631-3.00003-X",

    # ---- cited in the paper but previously missing -------------------------
    "Albert, R., Jeong, H., & Barab\u00e1si, A.-L. (2000). Error and attack tolerance of complex networks. *Nature, 406*(6794), 378\u2013382. https://doi.org/10.1038/35019019",
    "Avila, R. T., Guan, X., Kane, C. N., Cardoso, A. A., Batz, T. A., DaMatta, F. M., Jansen, S., & McAdam, S. A. M. (2022). Xylem embolism spread is largely prevented by interconduit pit membranes until the majority of conduits are gas-filled. *Plant, Cell & Environment, 45*(4), 1204\u20131215. https://doi.org/10.1111/pce.14253",
    "Balios, V. A., Fischer, K., Bawin, T., & Krause, K. (2025). One organ to infect them all: The *Cuscuta* haustorium. *Annals of Botany, 135*(5), 823\u2013840. https://doi.org/10.1093/aob/mcae208",
    "Barab\u00e1si, A.-L., & Albert, R. (1999). Emergence of scaling in random networks. *Science, 286*(5439), 509\u2013512. https://doi.org/10.1126/science.286.5439.509",
    "Berezin, Y., Bashan, A., Danziger, M. M., Li, D., & Havlin, S. (2015). Localized attacks on spatially embedded networks with dependencies. *Scientific Reports, 5*, 8934. https://doi.org/10.1038/srep08934",
    "Brodribb, T. J., Bienaim\u00e9, D., & Marmottant, P. (2016). Revealing catastrophic failure of leaf networks under stress. *Proceedings of the National Academy of Sciences, 113*(17), 4865\u20134869. https://doi.org/10.1073/pnas.1522569113",
    "Callaway, D. S., Newman, M. E. J., Strogatz, S. H., & Watts, D. J. (2000). Network robustness and fragility: Percolation on random graphs. *Physical Review Letters, 85*(25), 5468\u20135471. https://doi.org/10.1103/PhysRevLett.85.5468",
    "Clark, A. (2015). *Pillow (PIL Fork) documentation*. Readthedocs. https://buildmedia.readthedocs.org/media/pdf/pillow/latest/pillow.pdf",
    "Cochavi, A., Rapaport, T., Gendler, T., Karnieli, A., Eizenberg, H., Rachmilevitch, S., & Ephrath, J. E. (2017). Recognition of *Orobanche cumana* below-ground parasitism through physiological and hyperspectral measurements in sunflower (*Helianthus annuus* L.). *Frontiers in Plant Science, 8*, 909. https://doi.org/10.3389/fpls.2017.00909",
    "Cliff, N. (1993). Dominance statistics: Ordinal analyses to answer ordinal questions. *Psychological Bulletin, 114*(3), 494–509. https://doi.org/10.1037/0033-2909.114.3.494",
    "Dixon, W. J., & Mood, A. M. (1946). The statistical sign test. *Journal of the American Statistical Association, 41*(236), 557–566. https://doi.org/10.1080/01621459.1946.10501898",
    "Dorfman, R. (1979). A formula for the Gini coefficient. *The Review of Economics and Statistics, 61*(1), 146–149. https://doi.org/10.2307/1924845",
    "Dormann, C. F., Elith, J., Bacher, S., Buchmann, C., Carl, G., Carré, G., Marquéz, J. R. G., Gruber, B., Lafourcade, B., Leitão, P. J., Münkemüller, T., McClean, C., Osborne, P. E., Reineking, B., Schröder, B., Skidmore, A. K., Zurell, D., & Lautenbach, S. (2013). Collinearity: A review of methods to deal with it and a simulation study evaluating their performance. *Ecography, 36*(1), 27–46. https://doi.org/10.1111/j.1600-0587.2012.07348.x",
    "Kerby, D. S. (2014). The simple difference formula: An approach to teaching nonparametric correlation. *Comprehensive Psychology, 3*, 11.IT.3.1. https://doi.org/10.2466/11.IT.3.1",
    "Kruskal, W. H., & Wallis, W. A. (1952). Use of ranks in one-criterion variance analysis. *Journal of the American Statistical Association, 47*(260), 583–621. https://doi.org/10.1080/01621459.1952.10483441",
    "Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *The Annals of Mathematical Statistics, 18*(1), 50–60. https://doi.org/10.1214/aoms/1177730491",
    "Morris, T. P., White, I. R., & Crowther, M. J. (2019). Using simulation studies to evaluate statistical methods. *Statistics in Medicine, 38*(11), 2074–2102. https://doi.org/10.1002/sim.8086",
    "Pratt, J. W. (1959). Remarks on zeros and ties in the Wilcoxon signed rank procedures. *Journal of the American Statistical Association, 54*(287), 655–667. https://doi.org/10.1080/01621459.1959.10501526",
    "Dorogovtsev, S. N., Goltsev, A. V., & Mendes, J. F. F. (2008). Critical phenomena in complex networks. *Reviews of Modern Physics, 80*(4), 1275\u20131335. https://doi.org/10.1103/RevModPhys.80.1275",
    "Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall/CRC. https://doi.org/10.1201/9780429246593",
    "Freeman, L. C. (1977). A set of measures of centrality based on betweenness. *Sociometry, 40*(1), 35\u201341. https://doi.org/10.2307/3033543",
    "Griebel, A., Peters, J. M. R., Metzen, D., Maier, C., Barton, C. V. M., Speckman, H. N., Boer, M. M., Nolan, R. H., Choat, B., & Pendall, E. (2022). Tapping into the physiological responses to mistletoe infection during heat and drought stress. *Tree Physiology, 42*(3), 523\u2013536. https://doi.org/10.1093/treephys/tpab113",
    "Hagberg, A. A., Schult, D. A., & Swart, P. J. (2008). Exploring network structure, dynamics, and function using NetworkX. In *Proceedings of the 7th Python in Science Conference* (pp. 11\u201315). SciPy.",
    "Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., Wieser, E., Taylor, J., Berg, S., Smith, N. J., Kern, R., Picus, M., Hoyer, S., van Kerkwijk, M. H., Brett, M., Haldane, A., del R\u00edo, J. F., Wiebe, M., Peterson, P., \u2026 Oliphant, T. E. (2020). Array programming with NumPy. *Nature, 585*(7825), 357\u2013362. https://doi.org/10.1038/s41586-020-2649-2",
    "Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering, 9*(3), 90\u201395. https://doi.org/10.1109/MCSE.2007.55",
    "Jeschke, W. D., B\u00e4umel, P., R\u00e4th, N., Czygan, F.-C., & Proksch, P. (1994). Modelling of the flows and partitioning of carbon and nitrogen in the holoparasite *Cuscuta reflexa* Roxb. and its host *Lupinus albus* L.: II. Flows between host and parasite and within the parasitized host. *Journal of Experimental Botany, 45*(6), 801\u2013812. https://doi.org/10.1093/jxb/45.6.801",
    "Jiang, F., Jeschke, W. D., & Hartung, W. (2003). Water flows in the parasitic association *Rhinanthus minor*/*Hordeum vulgare*. *Journal of Experimental Botany, 54*(389), 1985\u20131993. https://doi.org/10.1093/jxb/erg212",
    "Kaga, Y., Yokoyama, R., Sano, R., Ohtani, M., Demura, T., Kuroha, T., Shinohara, N., & Nishitani, K. (2020). Interspecific signaling between the parasitic plant and the host plants regulate xylem vessel cell differentiation in haustoria of *Cuscuta campestris*. *Frontiers in Plant Science, 11*, 193. https://doi.org/10.3389/fpls.2020.00193",
    "Kaiser, B., Vogg, G., F\u00fcrst, U. B., & Albert, M. (2015). Parasitic plants of the genus *Cuscuta* and their interaction with susceptible and resistant host plants. *Frontiers in Plant Science, 6*, 45. https://doi.org/10.3389/fpls.2015.00045",
    "Katifori, E., Sz\u00f6ll\u0151si, G. J., & Magnasco, M. O. (2010). Damage and fluctuations induce loops in optimal transport networks. *Physical Review Letters, 104*(4), 048704. https://doi.org/10.1103/PhysRevLett.104.048704",
    "Loepfe, L., Martinez-Vilalta, J., Pi\u00f1ol, J., & Mencuccini, M. (2007). The relevance of xylem network structure for plant hydraulic efficiency and safety. *Journal of Theoretical Biology, 247*(4), 788\u2013803. https://doi.org/10.1016/j.jtbi.2007.03.036",
    "Matos, I. S., Boakye, M., Antonio, M., Carlos, S., Chu, A., Duarte, M. A., Echevarria, A., Fontao, A., Garcia, L., Huang, L., Johnson, B. C., Joshi, S., Kalantar, D., Madhavan, S., McDonough, S., Niewiadomski, I., Nguyen, N., Park, H. J., Pechuzal, C., \u2026 Blonder, B. (2024a). Leaf architecture and functional traits for 122 species at the University of California Botanical Garden at Berkeley. *Ecology, 105*(12), e4436. https://doi.org/10.1002/ecy.4436",
    "Matos, I. S., Boakye, M., Niewiadomski, I., Antonio, M., Carlos, S., Johnson, B. C., Chu, A., Echevarria, A., Fontao, A., Garcia, L., Kalantar, D., Madhavan, S., Mann, J., McDonough, S., Rohde, J., Scudder, M., Sharma, S., To, J., Tomaka, C., \u2026 Blonder, B. W. (2024b). Leaf venation network architecture coordinates functional trade-offs across vein spatial scales: Evidence for multiple alternative designs. *New Phytologist, 244*(2), 407\u2013425. https://doi.org/10.1111/nph.20037",
    "Memmott, J., Waser, N. M., & Price, M. V. (2004). Tolerance of pollination networks to species extinctions. *Proceedings of the Royal Society B: Biological Sciences, 271*(1557), 2605\u20132611. https://doi.org/10.1098/rspb.2004.2909",
    "Mou, Y., & Hayashi, Y. (2025). Vulnerable connectivity caused by local communities in spatial networks. *PLOS ONE, 20*, e0327203. https://doi.org/10.1371/journal.pone.0327203",
    "Mrad, A., Domec, J.-C., Huang, C.-W., Lens, F., & Katul, G. (2018). A network model links wood anatomy to xylem tissue hydraulic behaviour and vulnerability to cavitation. *Plant, Cell & Environment, 41*(12), 2718\u20132730. https://doi.org/10.1111/pce.13415",
    "Mrad, A., Johnson, D. M., Love, D. M., & Domec, J.-C. (2021). The roles of conduit redundancy and connectivity in xylem hydraulic functions. *New Phytologist, 231*(3), 996\u20131007. https://doi.org/10.1111/nph.17429",
    "Muraleedharan, V., Rajan, S. C., & Jaishanker, R. (2023). Determining the limits of traditional box-counting fractal analysis in leaf complexity studies. *Flora, 304*, 152300. https://doi.org/10.1016/j.flora.2023.152300",
    "Nardini, A., Ped\u00e1, G., & La Rocca, N. (2012). Trade-offs between leaf hydraulic capacity and drought vulnerability: Morpho-anatomical bases, carbon costs and ecological consequences. *New Phytologist, 196*(3), 788\u2013798. https://doi.org/10.1111/j.1469-8137.2012.04294.x",
    "Newman, M. E. J. (2003). The structure and function of complex networks. *SIAM Review, 45*(2), 167\u2013256. https://doi.org/10.1137/S003614450342480",
    "Newman, M. E. J., & Ziff, R. M. (2001). Fast Monte Carlo algorithm for site or bond percolation. *Physical Review E, 64*(1), 016706. https://doi.org/10.1103/PhysRevE.64.016706",
    "Noblin, X., Mahadevan, L., Coomaraswamy, I. A., Weitz, D. A., Holbrook, N. M., & Zwieniecki, M. A. (2008). Optimal vein density in artificial and real leaves. *Proceedings of the National Academy of Sciences, 105*(27), 9140\u20139144. https://doi.org/10.1073/pnas.0709194105",
    "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, \u00c9. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825\u20132830.",
    "Price, C. A., & Weitz, J. S. (2014). Costs and benefits of reticulate leaf venation. *BMC Plant Biology, 14*, 234. https://doi.org/10.1186/s12870-014-0234-2",
    "Ronellenfitsch, H., & Katifori, E. (2019). Phenotypes of vascular flow networks. *Physical Review Letters, 123*(24), 248101. https://doi.org/10.1103/PhysRevLett.123.248101",
    "Ronellenfitsch, H., Lasser, J., Daly, D. C., & Katifori, E. (2015). Topological phenotypes constitute a new dimension in the phenotypic space of leaf venation networks. *PLoS Computational Biology, 11*(12), e1004680. https://doi.org/10.1371/journal.pcbi.1004680",
    "Sack, L., Dietrich, E. M., Streeter, C. M., S\u00e1nchez-G\u00f3mez, D., & Holbrook, N. M. (2008). Leaf palmate venation and vascular redundancy confer tolerance of hydraulic disruption. *Proceedings of the National Academy of Sciences, 105*(5), 1567\u20131572. https://doi.org/10.1073/pnas.0709333105",
    "Scoffoni, C., Albuquerque, C., Brodersen, C. R., Townes, S. V., John, G. P., Bartlett, M. K., Buckley, T. N., McElrone, A. J., & Sack, L. (2017). Outside-xylem vulnerability, not xylem embolism, controls leaf hydraulic decline during dehydration. *Plant Physiology, 173*(2), 1197\u20131210. https://doi.org/10.1104/pp.16.01643",
    "Shao, S., Huang, X., Stanley, H. E., & Havlin, S. (2015). Percolation of localized attack on complex networks. *New Journal of Physics, 17*(2), 023049. https://doi.org/10.1088/1367-2630/17/2/023049",
    "Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality (complete samples). *Biometrika, 52*(3\u20134), 591\u2013611. https://doi.org/10.1093/biomet/52.3-4.591",
    "Shen, H., Hong, L., Ye, W., Cao, H., & Wang, Z. (2007). The influence of the holoparasitic plant *Cuscuta campestris* on the growth and photosynthesis of its host *Mikania micrantha*. *Journal of Experimental Botany, 58*(11), 2929\u20132937. https://doi.org/10.1093/jxb/erm168",
    "Skjegstad, L. E. J., & Kirkegaard, J. B. (2025). Modeling full-scale leaf venation networks. *PLOS Computational Biology, 21*(7), e1013292. https://doi.org/10.1371/journal.pcbi.1013292",
    "Tian, L., Bashan, A., Shi, D.-N., & Liu, Y.-Y. (2017). Articulation points in complex networks. *Nature Communications, 8*, 14223. https://doi.org/10.1038/ncomms14223",
    "Trajanovski, S., Mart\u00edn-Hern\u00e1ndez, J., Winterbach, W., & Van Mieghem, P. (2013). Robustness envelopes of networks. *Journal of Complex Networks, 1*(1), 44\u201362. https://doi.org/10.1093/comnet/cnt004",
    "Tyree, M. T., & Sperry, J. S. (1989). Vulnerability of xylem to cavitation and embolism. *Annual Review of Plant Physiology and Plant Molecular Biology, 40*, 19\u201338. https://doi.org/10.1146/annurev.pp.40.060189.000315",
    "Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., Kern, R., Larson, E., \u2026 Vázquez-Baeza, Y. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods, 17*(3), 261\u2013272. https://doi.org/10.1038/s41592-019-0686-2",
    "Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin, 1*(6), 80\u201383. https://doi.org/10.2307/3001968",
    "Xu, H., Blonder, B., Jodra, M., Malhi, Y., & Fricker, M. (2021). Automated and accurate segmentation of leaf venation networks via deep learning. *New Phytologist, 229*(1), 631\u2013648. https://doi.org/10.1111/nph.16923",
    "Zhang, Z., Shi, X., Xiang, X., Wang, C., Xiao, S., & Su, X. (2020). Bootstrap confidence intervals for the optimal cutoff point to bisect estimated probabilities from logistic regression. *Statistical Methods in Medical Research, 29*(6), 1514\u20131526. https://doi.org/10.1177/0962280219864998",
]


# Entries retained in this file but NOT rendered: nothing in the paper cites
# them (leftovers from the earlier holoparasite framing).  Delete a prefix from
# this list to put that reference back into the document.
UNCITED = (
    "Barry, L.,",
    "Bascos, E. M. A.,",
    "Boehm, H.",
    "Bozkurt, T. O.,",
    "Chen, Y., Wu, H.,",
    "Dawson, T. E.,",
    "Denny, M.",
    "De Swaef, T.,",
    "Dixon, H. H. (1894)",
    "Dixon, H. H., & Joly",
    "Fernández-Aparicio",
    "Gogoi, A.,",
    "Gooch, J. W.",
    "Goyet, V.,",
    "Hatt, S. A.,",
    "Kaiser, B., Vogg, G.,",   # gradient re-attributed on p.7; no longer cited
    "Haworth, M.,",
    "Hegenauer, V.,",
    "Henry, A.,",
    "Lambio, I. A. F.,",
    "Ma, J., Zhao, Z.,",
    "Malabrigo, P. L.,",
    "Maqsood, A.,",
    "Mateus, N. S.,",
    "McCulloh, K. A., Sperry, J. S., & Adler",
    "McCulloh, K. A., Sperry, J. S., Meinzer",
    "Murray, C. D.",
    "Nabity, P. D.,",
    "Obico, J. J. A.,",
    "Ossa, C. G.,",
    "Pelser, P. B.,",
    "Pérez-de-Luque, A.",
    "Qaderi, M. M.,",
    "Saleem, M.,",
    "Sarun, H.",
    "Sharma, B. P.,",
    "Sullivan, J.",
    "Twyford, A. D.",
    "Voegele, R. T.,",
    "Zagorchev, L.,",
    "Zhang, J. X., & Hoshino",
)


def sort_key(entry):
    """APA letter-by-letter ordering on the author string, then year."""
    plain = entry.replace("*", "")
    head = plain.split(" (")[0]
    head = unicodedata.normalize("NFKD", head)
    head = "".join(c for c in head if not unicodedata.combining(c))
    head = re.sub(r"[^A-Za-z]", "", head).lower()
    m = re.search(r"\((\d{4}[a-z]?)", plain)
    return (head, m.group(1) if m else "")


def add_entry(doc, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Inches(0.5)
    pf.first_line_indent = Inches(-0.5)          # hanging indent
    pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    for i, seg in enumerate(re.split(r"\*", text)):
        if not seg:
            continue
        run = p.add_run(seg)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        run.italic = bool(i % 2)
    return p


def main():
    doc = Document()
    doc.styles["Normal"].font.name = "Times New Roman"
    doc.styles["Normal"].font.size = Pt(12)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1)

    cited = [e for e in ENTRIES if not e.startswith(UNCITED)]
    dropped = len(ENTRIES) - len(cited)
    assert dropped == len(UNCITED), f"prefix mismatch: dropped {dropped} of {len(UNCITED)}"

    for entry in sorted(cited, key=sort_key):
        add_entry(doc, entry)

    out = r"c:\Users\Nicko\HOLOPARASITIC\DISTRICT STF - BIBLIOGRAPHY.docx"
    doc.save(out)
    print(f"wrote {out} ({len(cited)} references; {dropped} uncited removed)")


if __name__ == "__main__":
    main()
