library(reticulate)
library(dplyr)
library(magrittr)
library(purrr)


apply_f <- function(df, f, subset_vars=FALSE) {
  if (is.logical(subset_vars)) {
    df %>% bind_cols(map_df(.$data, ~map(., f)))
  } else {
    df %>% bind_cols(
      map_df(.$data, 
             ~map(set_names(.[subset_vars], subset_vars), 
                  f)))
  }
}


use_python("/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4", required=TRUE)
sys <- import("sys")
sys$version_info

main_path = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
id_path = "/Users/zburchill/Documents/workspace2/python3_files/src/valid_series_ids"
db_file = "first"

source_python(paste0(main_path, "load_for_r.py"))
list_of_dicts <- load_dicts(paste0(main_path, db_file),
                            id_path)

########################################################
l = list_of_dicts
nrows = length(l)
df <- data.frame(z = rep.int(0, nrows)) %>%
  tibble::as_tibble()
df$data <- l
df %<>%
  mutate(id = purrr::map(data, ~.$id) %>%
           purrr::simplify())
df.n <- df %>%
  bind_cols(map_df(.$data, ~map(., length))) %>%
  select(-data)
summary(df.n)
df.n %>%
  summarize_all(~length(unique(.))) %>%
  as.data.frame()
# User_ratings should have 2 lengths
# Check for "Anthology" in artists and authors
# list_stats should have two (can't have 'completed' an unfinished work)

df2 <- df %>%
  mutate(x = map(data, ~.$list_stats),
         y = map(data, ~paste0(.$list_stats, collapse=";")) %>% 
           simplify(),
         w = map(data, ~paste0(sort(names(.$list_stats)), collapse=";")) %>%
           simplify() %>% factor(),
         n = map(data, ~length(.$list_stats)) %>% 
           simplify()) %>%
  select(-z, -data)

df2 %>% filter(n > 1) %>% arrange(-n) %>% as.data.frame()


# check `list_stats`:
map(df$data, ~paste0(sort(names(.$list_stats)), collapse=";")) %>%
  simplify() %>% factor()



##############




hmmm <- function(x, y) {
  purrr::map(x, ~length(y$authors)) %>%
    purrr::simplify()
}

assemble_data_frame <- function(l) {
  nrows = length(l)
  df <- data.frame(z = rep.int(0, nrows)) %>%
    tibble::as_tibble()
  df$data <- l
  df %>%
    mutate(id = purrr::map(l, ~.$id)) %>%
    mutate(id = purrr::map(l, ~.$id) %>%
             purrr::simplify())
    
    
    
    mutate_at(vars("authors"), ~hmmm(l,.))
    
  purrr::map(l, ~length(.$authors)) %>%
    purrr::simplify())      
      
      authors = purrr::map(l,~paste(.$authors,collapse=";")) %>%
             purrr::simplify(),
           
             purrr::simplify(),
           original_pub = purrr::map(l,~paste(.$original_pub,collapse=";")) %>%
             purrr::simplify()) %>% 
    select(id, authors, original_pub)
  
  
}



df %>%
  mutate(authors = purrr::map(l,~paste(.$authors,collapse=";")) %>%
           purrr::simplify(),
         id = purrr::map(l,~.$id) %>%
           purrr::simplify(),
         original_pub = purrr::map(l,~paste(.$original_pub,collapse=";")) %>%
           purrr::simplify()) %>% 
  select(id, authors, original_pub)

df %>%
  mutate(authors = purrr::map(l, ~paste(.$authors,collapse=";")) %>%
           purrr::simplify(),
         nauthors = purrr::map(l,~length(.$authors)) %>%
                    purrr::simplify()) %>%
  filter(nauthors > 1)



library(ggplot2)

d <- tibble(
  l = list(list("a"=list("a1","a2","a3","a4"), 
                "b"=list("b1","b2","b3")),
           list("a"=list("x1","x2"), 
                "b"=list("y3")))
)

d2 <- d
d2$n_a <- c(4, 2)
d2$n_b <- c(3, 1)



apply_f <- function(df, f, subset_vars=FALSE) {
  if (is.logical(subset_vars)) {
    df %>% bind_cols(map_df(.$data, ~map(., f)))
  } else {
    df %>% bind_cols(
      map_df(.$data, 
             ~map(set_names(.[subset_vars], subset_vars), 
                                     length)))
  }
}

subset_var = c('a', "b")  
d %>% bind_cols(map_df(.$l, ~map(set_names(.[subset_var], subset_var), 
                                  length)))




l = list(list("a"=c("a1","a2","a3"), "b"=c("b1","b2","b3")),
      list("x"=c("x1","x2","x3"), "y"=c("y1","y2","y3")))







d <- tibble(
  l = list(list("a"=list("a1","a2","a3","a4"), 
                "b"=list("b1","b2","b3")),
           list("a"=list("x1","x2"), 
                "b"=list("y3")))
)
d <- tibble(
  l = list(list("a"=list("a1","a2","a3","a4")),
           list("a"=list("x1","x2"), 
                "b"=list("y3")))
)

d %>% bind_cols(., map_df(.$l, ~ as.list(lengths(.))))
d %>% map_df(.$l, ~ as.list(lengths(.)))


map_df(d$l, ~ as.list(lengths(.))))

d %>% bind_cols(map_df(.$l, ~map(., length)))

mtcars %>%
  split(.$cyl) %>%
  map(~ lm(mpg ~ wt, data = .x)) %>%
  map_df(~ as.data.frame(t(as.matrix(coef(.)))))


