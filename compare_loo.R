rm(list=ls())

#######################################################################
#create dictionaries for data, its associated functions and filename
#######################################################################
dict_input = c("comemp", "compop", "comrev", "comtrans", "resemp", "respop",  "resrev", "restrans")
#dict_func = c("pow", "pow", "pow", "cubic", "bell", "bell", "pow", "cubic")
dict_func_chg = c("bell", "line", "bell", "cubic", "bell", "bell",  "cubic", "pow")
#test_func = c("pow", "pow", "pow", "pow", "pow", "pow", "pow", "pow")
#test_func = c("line", "line", "line", "line", "line", "line", "line", "line")
#test_func = c("bell", "bell", "bell", "bell", "bell", "bell", "bell", "bell")
test_func = c("cubic", "cubic", "cubic", "cubic", "cubic", "cubic", "cubic", "cubic")

#use_func = dict_func
#use_func = dict_func_chg
use_func = test_func

#foldername = "./j_noch/"
foldername = "./j_change/"

#function list
dict_l = length(dict_input)

func_l = list()
#try_fun = character(dict_l)


# point drawing data
out_data = numeric()


####################
#leave_one_out
#######################

loo = function(func, new_x, new_y){
  pred_y = func(new_x)
  abs(new_y - pred_y)
} 

pow = function(data){
    #creating smotthed data

    #my_data$n_x = my_data$n_x/max(my_data$n_x)
    data$log_y = log(data$y)
    smod = lm(log_y ~ log(n_x), data = data[-1, ])
    n_data = seq (0, max(data$n_x), length.out = 100)
    n_data = data.frame(n_data)
    n_data$n_x = seq (0, max(data$n_x), length.out = 100)
    n_data$new_y = predict(smod, newdata=n_data)
    a = smod$coef["(Intercept)"]
    b = smod$coef["log(n_x)"]
    
    #try_fun = paste0("exp(", a, ") * (x+1) ^", b, sep = "")
    try_fun = paste0(a, "+", b, "* log(x+1)", sep = "")
    test_fun = function (x) {
      #exp(a) * exp(b * x)
      eval(parse(text = try_fun)) 
  }
  return(test_fun)
}

line = function(data){
  #creating smotthed data
  
  #my_data$n_x = my_data$n_x/max(my_data$n_x)
  smod = lm(y ~ n_x, data = data)
  n_data = seq (0, max(data$n_x), length.out = 100)
  n_data = data.frame(n_data)
  n_data$n_x = seq (0, max(data$n_x), length.out = 100)
  n_data$new_y = predict(smod, newdata=n_data)
  a = smod$coef["(Intercept)"]
  b = smod$coef["n_x"]
  
  try_fun = paste0(a, " + ", b , " * x", sep = "")
  
  test_fun = function (x) {
    #a + b * x
    eval(parse(text = try_fun))} 
  return(test_fun)
}

bell = function(data){

  data$x2 = data$n_x ** 2
  
  smod = lm(y ~ n_x + x2, data = data)
  n_data = seq (0, max(data$n_x), length.out = 100)
  n_data = data.frame(n_data)
  n_data$n_x = seq (min(data$n_x), max(data$n_x), length.out = 100)
  n_data$x2 = n_data$n_x ** 2
  n_data$new_y = predict(smod, newdata=n_data)
  
  
  a = smod$coef["(Intercept)"]
  b = smod$coef["n_x"]
  c = smod$coef["x2"]
  
  try_fun = paste0(a, "+", b, " * x + ", c, " * x ** 2", sep = "")
  
  test_fun = function (x) {
    #a + b * x + c * x ** 2}
    eval(parse(text = try_fun))
  }
  
  return(test_fun)
}

cubic = function(data){
  
  data$x2 = data$n_x ** 2
  data$x3 = data$n_x ** 3
  
  smod = lm(y ~ n_x + x2 + x3, data = data)
  n_data = seq (0, max(data$n_x), length.out = 100)
  n_data = data.frame(n_data)
  n_data$n_x = seq (min(data$n_x), max(data$n_x), length.out = 100)
  n_data$x2 = n_data$n_x ** 2
  n_data$x3 = n_data$n_x ** 3
  n_data$new_y = predict(smod, newdata=n_data)
  a = smod$coef["(Intercept)"]
  b= smod$coef["n_x"]
  c = smod$coef["x2"]
  d = smod$coef["x3"]
  
  try_fun = paste0(a, " + ", b, " * x +", c, " * x ** 2 +", d, " * x ** 3", sep = "")
  
  test_fun = function (x) {
    #a + b * x + c * x ** 2 + d * x ** 3}
    eval(parse(text = try_fun))
  }
  
  return(test_fun)
}

#######################################################################
#read data and execute
#######################################################################
for (i in 1:8) {

#for (i in 1:4) {
#for (i in 1:dict_l){
  
  data_name = paste0(foldername,  dict_input[i],  ".csv", sep = "")
  #out_name = paste0("./Graph_out/",   dict_input[i],   ".png")
  my_data = read.csv(data_name)
  #eval(parse(text=qaqc[i])) 
  my_data$y = pmax(my_data$y, rep(0.0001, length(my_data$y)))
  std_coef = max(my_data$x)-min(my_data$x)
  my_data$n_x = (my_data-min(my_data$x))$x/std_coef + 1
  
  if (use_func[i] == "pow"){
    
    avg_loo = rep(0, length(my_data[, 1]))
                  
    for (j in 1:length(my_data[, 1])){
      fun_out = pow(my_data[-j, ])
      new_data = my_data$n_x[j]
      avg_loo[i] = loo(fun_out, log(new_data), log(my_data$y[j]))
    }
    print(paste0(dict_input[i], " ", use_func[i], "loo=", mean(avg_loo)))
     
  }
  
  else if (use_func[i] == "line"){
    
    avg_loo = rep(0, length(my_data[, 1]))
    
    for (j in 1:length(my_data[, 1])){
      fun_out = line(my_data[-j, ])
      new_data = my_data$n_x[j]
      avg_loo[i] = loo(fun_out, new_data, my_data$y[j])
    }
    print(paste0(dict_input[i], " ", use_func[i], "loo=", mean(avg_loo)))
    
  }
  
  else if (use_func[i] == "bell"){
    
    avg_loo = rep(0, length(my_data[, 1]))
    
    for (j in 1:length(my_data[, 1])){
      fun_out = bell(my_data[-j, ])
      new_data = my_data$n_x[j]
      avg_loo[i] = loo(fun_out, new_data, my_data$y[j])
    }
    print(paste0(dict_input[i], " ", use_func[i], "loo=", mean(avg_loo)))
    
  }
    
  
else if (use_func[i] == "cubic"){
  
  avg_loo = rep(0, length(my_data[, 1]))
  
  for (j in 1:length(my_data[, 1])){
    fun_out = cubic(my_data[-j, ])
    new_data = my_data$n_x[j]
    avg_loo[i] = loo(fun_out, new_data, my_data$y[j])
  }
  print(paste0(dict_input[i], " ", use_func[i], "loo=", mean(avg_loo)))
  
  }
}
    
