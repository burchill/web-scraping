library(jsonlite)
library(dplyr)
library(magrittr)
library(purrr)


# I don't quite remember what this does...
apply_f <- function(df, f, subset_vars=FALSE) {
  if (is.logical(subset_vars)) {
    df %>% bind_cols(map_df(.$data, ~map(., f)))
  } else {
    df %>% bind_cols(
      map_df(.$data, 
             ~map(set_names(.[subset_vars], subset_vars), 
                  f)))
}}

main_path = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
metadata_db_file = "everything_json.json"
# issue_db_file = "first_1891_issues"

metadata_list <- fromJSON(paste0(main_path, metadata_db_file), flatten=FALSE)


make_issue_dataframe <- function(l) {
  df <- l %>%
    purrr::keep(~length(.) < 100) %>% # filter out weirdos
    purrr::imap_dfr(function(series, series_id) {
      purrr::imap_dfr(series, function(page, pagenum){
        purrr::map_dfr(page, function(release) {
          as.data.frame(t(release), stringsAsFactors=FALSE)
        }) %>%
          mutate(PageNumber = pagenum)
      }) %>%
        mutate(SeriesID = series_id)
    }) %>%
    transmute(Date = lubridate::mdy(V1),
              Title = V2,
              Volume = V3,
              Chapter = V4,
              Groups = V5,
              PageNumber, SeriesID) %>%
    filter(!is.na(Date))
} 
issue_df <- make_issue_dataframe(issue_dict)














########################################################
l = metadata_list
nrows = length(l)
df <- data.frame(z = 1:nrows) %>%
  tibble::as_tibble()
df$data <- l
df$id <- names(l)
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



##########################################################

############### NEW stuff ###############################







###################### older stuff: #########################




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


