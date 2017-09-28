rm(list=ls())

library(ggplot2)
#######################################################################
#create dictionaries for data, its associated functions and filename
#######################################################################
dict_input = c("comemp", "compop", "comrev", "comtrans", "resemp", "respop",  "resrev", "restrans")
dict_func = c("pow", "pow", "pow", "cubic", "bell", "bell", "pow", "cubic")
dict_func_chg = c("bell", "line", "bell", "cubic", "bell", "bell",  "cubic", "pow")

#use_func = dict_func
use_func = dict_func_chg


foldername = "./j_noch/"
foldername = "./j_change/"

#function list
dict_l = length(dict_input)

func_l = list()
try_fun = character(dict_l)


#######################################################################
#QAQC!
#######################################################################

qaqc = character(dict_l)
#comemp nochange
qaqc[1] = "my_data = my_data[-nrow(my_data),]"
qaqc[2] = "my_data = my_data[-nrow(my_data),]"
qaqc[3] = "my_data = my_data[-nrow(my_data),]"
qaqc[4] = "my_data = my_data[-nrow(my_data),]"
qaqc[5] = "my_data = my_data[-nrow(my_data),]"
qaqc[6] = "my_data = my_data[-nrow(my_data),]"
qaqc[7] = "my_data = my_data[-nrow(my_data),]"
qaqc[8] = "my_data = my_data[-nrow(my_data),]"

# #comemp change
# qaqc[1] = "my_data = my_data[-1,]; my_data = my_data[-nrow(my_data),]"
# qaqc[2] = "my_data = my_data[-1,]"
# qaqc[3] = "my_data = my_data[-nrow(my_data),]"
# qaqc[4] = "my_data = my_data[-nrow(my_data),]"
# qaqc[5] = "my_data = my_data[-1,]; my_data = my_data[-nrow(my_data),]"
# qaqc[6] = "my_data = my_data[-1,]"
# qaqc[7] = "my_data = my_data[-1,]"
# qaqc[8] = ""

#function variable initialization
#a = rep (1, dict_l)
#b = rep (1, dict_l)
#c = rep (1, dict_l)
#d = rep (1, dict_l)

# point drawing data
out_data = numeric()



#######################################################################
#read data and execute
#######################################################################

for (i in 1:4) {
#for (i in 1:dict_l){
  
  data_name = paste0(foldername,  dict_input[i],  ".csv", sep = "")
  out_name = paste0("./Graph_out/",   dict_input[i],   ".png")
  my_data = read.csv(data_name)
  #eval(parse(text=qaqc[i])) 
  my_data$y = pmax(my_data$y, rep(0.0001, length(my_data$y)))
  
  if (use_func[i] == "pow"){
    #creating smotthed data
    std_coef = max(my_data$x)-min(my_data$x)
    my_data$n_x = (my_data-min(my_data$x))$x/std_coef + 1
    #my_data$n_x = my_data$n_x/max(my_data$n_x)
    my_data$log_y = log(my_data$y)
    smod = lm(log_y ~ log(n_x), data = my_data)
    new_data = seq (0, max(my_data$n_x), length.out = 100)
    new_data = data.frame(new_data)
    new_data$n_x = seq (0, max(my_data$n_x), length.out = 100)
    new_data$new_y = predict(smod, newdata=new_data)
    a = smod$coef["(Intercept)"]
    b = smod$coef["log(n_x)"]
    
    try_fun[i] = paste0("exp(", a, ") * (x+1) ^", b, sep = "")
    test_fun = function (x) {
      #exp(a) * exp(b * x)
      eval(parse(text = try_fun)) }

    # func_l = c(func_l,test_fun)

    #draw graph
    
    lab = paste("y=",round(exp(a), digits = 5), "x^", round(b, digits = 1),
                             sep = "")
    
    lab = print(lab)
    
    lab_x = mean(my_data$n_x)

    p1 = ggplot(data = my_data, aes(x=n_x,y=y)) + geom_point() +
      labs(x = "travel time to centers in min", y = "Percent of commerical cells") +
      theme(text = element_text(size=15), axis.text = element_text(size=10),
            axis.title=element_text(size=15)) + ggtitle("Percent of residential cells to travel time") +
      stat_function(fun=test_fun , color ="blue") +
      annotate("text", x = mean(lab_x), y = 0.2,
               label = lab)
    my_data$n_x = my_data$n_x - 1
  }
  
  else if (use_func[i] == "line"){
    #creating smotthed data
    std_coef = max(my_data$x)-min(my_data$x)
    my_data$n_x = (my_data-min(my_data$x))$x/std_coef
    #my_data$n_x = my_data$n_x/max(my_data$n_x)
    smod = lm(y ~ n_x, data = my_data)
    new_data = seq (0, max(my_data$n_x), length.out = 100)
    new_data = data.frame(new_data)
    new_data$n_x = seq (0, max(my_data$n_x), length.out = 100)
    new_data$new_y = predict(smod, newdata=new_data)
    a = smod$coef["(Intercept)"]
    b = smod$coef["n_x"]
    
    try_fun[i] = paste0(a, " + ", b , " * x", sep = "")
    
    test_fun = function (x) {
      #a + b * x
      eval(parse(text = try_fun))}

    # func_l = c(func_l, test_fun)

    #draw graph
    
    lab = paste("y=",round(a, digits = 3), "+", round(b, digits = 1),
                "x", sep = "")
    
    lab = print(lab)
    
    lab_x = mean(my_data$n_x)
    
    p1 = ggplot(data = my_data, aes(x=n_x,y=y)) + geom_point() +
      labs(x = "travel time to centers in min", y = "Percent of commerical cells") +
      theme(text = element_text(size=15), axis.text = element_text(size=10),
            axis.title=element_text(size=15)) + ggtitle("Percent of residential cells to travel time") +
      stat_function(fun=test_fun , color ="blue") +
      annotate("text", x = mean(lab_x), y = 0.2,
               label = lab)
  }
  
  else if (use_func[i] == "log"){
    #creating smotthed data
    std_coef = max(my_data$x)-min(my_data$x)
    my_data$n_x = (my_data$x-min(my_data$x))/std_coef+1
    #my_data$n_x = my_data$n_x/max(my_data$n_x)
    smod = lm(y ~ log(n_x), data = my_data)
    new_data = seq (min(my_data$n_x), max(my_data$n_x), length.out = 100)
    new_data = data.frame(new_data)
    new_data$n_x = seq (min(my_data$n_x), max(my_data$n_x), length.out = 100)
    new_data$new_y = predict(smod, newdata=new_data)
    a = smod$coef["(Intercept)"]
    b = smod$coef["log(n_x)"]
    
    try_fun[i] = paste0(a, " + ", b, " * log(x+1)")
    
    test_fun = function (x) {
      #a + b * log(x)
      eval(parse(text = try_fun))}

    # func_l = c(func_l,test_fun)

    #draw graph
    
    lab = paste("y=",round(exp(a), digits = 3), "+", round(b, digits = 1), "log(x)", sep = "")
    
    lab = print(lab)
    
    lab_x = mean(my_data$n_x)
    
    p1 = ggplot(data = my_data, aes(x=n_x,y=y)) + geom_point() +
      labs(x = "travel time to centers in min", y = "Percent of commerical cells") +
      theme(text = element_text(size=15), axis.text = element_text(size=10),
            axis.title=element_text(size=15)) + ggtitle("Percent of residential cells to travel time") +
      stat_function(fun=test_fun , color ="blue") +
      annotate("text", x = mean(lab_x), y = 0.2,
               label = lab)
    my_data$n_x = my_data$n_x - 1
  }
  
  
  else if (use_func[i] == "bell"){
    #creating smotthed data
    std_coef = max(my_data$x)-min(my_data$x)
    my_data$n_x = (my_data-min(my_data$x))$x/std_coef
    #my_data$n_x = my_data$n_x/max(my_data$n_x)
    my_data$x2 = my_data$n_x ** 2
    
    smod = lm(y ~ n_x + x2, data = my_data)
    new_data = seq (0, max(my_data$n_x), length.out = 100)
    new_data = data.frame(new_data)
    new_data$n_x = seq (min(my_data$n_x), max(my_data$n_x), length.out = 100)
    new_data$x2 = new_data$n_x ** 2
    new_data$new_y = predict(smod, newdata=new_data)
    
    
    a = smod$coef["(Intercept)"]
    b = smod$coef["n_x"]
    c = smod$coef["x2"]
    
    try_fun[i] = paste0(a, "+", b, " * x + ", c, " * x ** 2", sep = "")
    
    test_fun = function (x) {
      #a + b * x + c * x ** 2}
    eval(parse(text = try_fun))
      }


    # func_l = c(func_l, test_fun)

    #draw graph
    
    lab = paste("y=",round(a, digits = 3), "+", round(b, digits = 3), "x +", 
                round(c, digits = 3), "x^2", sep = "")
    
    lab = print(lab)
    
    lab_x = mean(my_data$n_x)
    
    p1 = ggplot(data = my_data, aes(x=n_x,y=y)) + geom_point() +
      labs(x = "travel time to centers in min", y = "Percent of commerical cells") +
      theme(text = element_text(size=15), axis.text = element_text(size=10),
            axis.title=element_text(size=15)) + ggtitle("Percent of residential cells to travel time") +
      stat_function(fun=test_fun , color ="blue") +
      annotate("text", x = mean(lab_x), y = 0.2,
               label = lab)
  }
  
  else if (use_func[i] == "cubic"){
    #creating smotthed data
    std_coef = max(my_data$x)-min(my_data$x)
    my_data$n_x = (my_data-min(my_data$x))$x/std_coef
    #my_data$n_x = my_data$n_x/max(my_data$n_x)
    my_data$x2 = my_data$n_x ** 2
    my_data$x3 = my_data$n_x ** 3
    
    smod = lm(y ~ n_x + x2 + x3, data = my_data)
    new_data = seq (0, max(my_data$n_x), length.out = 100)
    new_data = data.frame(new_data)
    new_data$n_x = seq (min(my_data$n_x), max(my_data$n_x), length.out = 100)
    new_data$x2 = new_data$n_x ** 2
    new_data$x3 = new_data$n_x ** 3
    new_data$new_y = predict(smod, newdata=new_data)
    a = smod$coef["(Intercept)"]
    b= smod$coef["n_x"]
    c = smod$coef["x2"]
    d = smod$coef["x3"]
    
    try_fun[i] = paste0(a, " + ", b, " * x +", c, " * x ** 2 +", d, " * x ** 3", sep = "")
    
    test_fun = function (x) {
      #a + b * x + c * x ** 2 + d * x ** 3}
      eval(parse(text = try_fun))
      }

    # func_l = c(func_l,test_fun)

    #draw graph
    
    lab = paste("y=",round(a, digits = 2), "+", round(b, digits = 2), "x +", 
                round(c, digits = 2), "x^2 +" , round(d, digits = 2), "x^3", sep = "")
    
    lab = print(lab)
    
    lab_x = mean(my_data$n_x)
    
    p1 = ggplot(data = my_data, aes(x=n_x,y=y)) + geom_point() +
      labs(x = "travel time to centers in min", y = "Percent of commerical cells") +
      theme(text = element_text(size=15), axis.text = element_text(size=10),
            axis.title=element_text(size=15)) + ggtitle("Percent of residential cells to travel time") +
      stat_function(fun=test_fun , color ="blue") +
      annotate("text", x = mean(lab_x), y = 0.2,
               label = lab)
    
    
    
  } 
  
  out_data = cbind(out_data, my_data$n_x, my_data$y)
}

out_data = data.frame (x = c(out_data[,1], out_data[,3], out_data[,5], out_data[,7]),
                       y = c(out_data[,2],out_data[,4], out_data[,6],out_data[,8]),
                       tag = c(rep("employment", length(out_data[,1])), 
                               rep("population", length(out_data[,3])),
                               rep("reviews", length(out_data[,5])),
                               rep("accessbility", length(out_data[,7])))) 



func_l = c(func_l, function (x) {eval(parse(text = try_fun[1]))})
func_l = c(func_l, function (x) {eval(parse(text = try_fun[2]))})
func_l = c(func_l, function (x) {eval(parse(text = try_fun[3]))})
func_l = c(func_l, function (x) {eval(parse(text = try_fun[4]))})



p2 = ggplot(data = out_data, aes(x=x, y=y, color = tag, shape = tag, linetype = tag)) + 
  theme_bw() + 
  geom_point(size = 3) +
  theme(text = element_text(size=15), axis.text = element_text(size=15),
        axis.title=element_text(size=15)) + ggtitle("Probability of changing to commercial vs. attractor values") +
  stat_function(fun=func_l[[1]] , aes(linetype = "employment", color = "employment")) +
  stat_function(fun=func_l[[2]] , aes(linetype = "population", color = "population"))  +
  stat_function(fun=func_l[[3]] , aes(linetype = "reviews", color = "reviews"))  +
  stat_function(fun=func_l[[4]] , aes(linetype = "accessbility", color = "accessbility"))  +
  scale_colour_manual(name = "attractor type",
                      labels = c("accessbility", "employment", "population", "reviews"),
                      values = c(1, 2, 9, 4)) +   
  scale_shape_manual(name = "attractor type",
                     labels = c("accessbility", "employment", "population", "reviews"),
                     values = c(1, 2, 5, 4)) +
  scale_linetype_manual(name = "attractor type",
                        labels = c("accessbility", "employment", "population", "reviews"),
                        values = c(1, 2, 3, 4)) +
  labs(
    x = "Normalized attractor values",
    y = "Probability of changing to commercial"
  ) +
  scale_x_continuous(limits = c(0, 1)) +
  scale_y_continuous(limits = c(0, max(out_data$y)))


p2

# p1 = ggplot(data = my_data, aes(x = n_x, y = y)) + geom_point(shape = 1, size = 3, color = 2) +
#   theme_bw() + 
#   labs(x = "Population attraction value", y = "Frequency of residential land-use") +
#   theme(text = element_text(size=15), axis.text = element_text(size=15),
#         axis.title=element_text(size=15)) + 
#   ggtitle("Residential land-use to population attraction value") +
#   stat_function(fun=test_fun) +
#   scale_y_continuous(limits = c(0, max(my_data$y)))
# 
# p1
#




#   my_data$x2 = my_data$x ** 2
#   my_data$x3 = my_data$x ** 3
#   my_data$x4 = my_data$x ** 4
#   smod = lm(y ~ x + x2 + x3, data = my_data)
#   new_data = seq (0, 100, length.out = 100)
#   new_data = data.frame(new_data)
#   new_data$x_new = seq (0, 100, length.out = 100)
#   new_data$x = new_data$x_new
#   new_data$x2 = new_data$x_new ** 2
#   new_data$x3 = new_data$x_new ** 3
#   new_data$x4 = new_data$x_new ** 4
#   new_data$new_y = predict(smod, newdata=new_data)
#   #my_data$new_y = new_data$new_y 
#   #my_data$new_y[my_data$new_y < 0] = 0 
#   a = smod$coef["(Intercept)"]
#   b = smod$coef["x"]
#   c = smod$coef["x2"]
#   d = smod$coef["x3"]
#   #e = smod$coef["x4"]
#   test_fun = function (x) {
#     a + b*x + c*x^2 + d*x^3}
# 
# 
# 
# lab = paste("y=",round(a, digits = 1), "+", round(b, digits = 2), 
#                         "x","+", round(c, digits = 3), "x^2","+", round(d, digits = 7) , 
#                         "x^3", sep = "")
# lab = print(lab)
# 
# p1 = ggplot(data = my_data, aes(x=x,y=y)) + geom_point() + 
#   labs(x = "travel time to centers in min", y = "Percent of commerical cells") +
#   theme(text = element_text(size=15), axis.text = element_text(size=10),
#         axis.title=element_text(size=15)) + ggtitle("Percent of residential cells to travel time") +
#   stat_function(fun=test_fun , color ="blue") +
#   annotate("text", x = 40, y = 0.2, 
#            label = lab)
# 
# 
# p1
