rm(list=ls())
if(!is.null(dev.list())) dev.off()
library(ggplot2)
library(tidyverse)
library(ggpubr)

cd <- read.csv("csv_density.csv", header=TRUE)
rownames(cd) <- cd[,1]
cd[,1] = NULL
cd = subset(cd, component_size > 2)

graph_density_plot <- ggplot(cd, aes(y = repo_name, x = subgraph_density)) + 
  geom_boxplot()

# -----------------

csd = read.csv("csv_component_size.csv", header=TRUE)
#csd = subset(csd, repo_name == "amphp-amp")
rownames(csd) = csd[,1]
csd[,1] = NULL

connected_component_sizes_plot <- ggplot(csd, aes(y = repo_name, x = component_size)) +
  geom_violin() + scale_x_log10() + geom_point(alpha = 0.3)

# ----------------

fd = read.csv("csv_fixes.csv", header=TRUE)
rownames(fd) = fd[,1]
fd[,1] = NULL

fixes_relationship <- ggplot(fd, aes(y = repo_name, x = percentage)) +
  geom_boxplot() + 
  stat_summary(fun=mean, geom = "point", shape=20, size=2, color="red")

# -----------------

wd = read.csv("csv_work_done_after_merge.csv", header=TRUE)
rownames(wd) = wd[,1]
wd[,1] = NULL

work_done_after_merge <- ggplot(wd, aes(y = repo_name, x = percentage)) + 
  geom_boxplot() + 
  stat_summary(fun=mean, geom = "point", shape=20, size=2, color="red")

# ----------------

dd = read.csv("csv_component_diameter.csv", header=TRUE)
rownames(dd) = dd[, 1]
dd[,1] = NULL

graph_diameter_density <- ggplot(dd, aes(x=component_size, y=subgraph_density)) + 
  geom_point() + 
  scale_x_log10()
graph_diameter_order <- ggplot(dd, aes(x=component_size, y=component_diameter)) + 
  geom_point() + 
  scale_x_log10()

corr_size_density <- ggscatter(dd, x = "component_size", y = "subgraph_density", 
                                add = "none", conf.int = FALSE,
                                cor.coef = FALSE, cor.method = "pearson") + 
  scale_x_log10() +
  geom_function(fun = function(x) 1/x)

corr_size_diameter <- ggscatter(dd, x = "component_size", y = "component_diameter", 
          add = "none", conf.int = FALSE,
          cor.coef = FALSE, cor.method = "pearson") + 
  scale_x_log10() + 
  #geom_abline(intercept = 1, slope = 1) +
  geom_function(fun = function(x) x - 1, ) +
  ylim(0, 50)

#-------------

gs = read.csv("csv_component_size.csv", header=TRUE)
rownames(gs) = gs[, 1]
gs[,1] = NULL

component_size_plot <- ggplot(gs, aes(component_size)) + geom_bar(fill = "#0073C2FF") +
  theme_pubclean()

component_size_plot[component_size_plot$data == 0] <- NA

#plot(corr_size_diameter)
#plot(corr_size_density)

