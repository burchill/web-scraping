library(reticulate)
library(dplyr)
library(magrittr)
library(purrr)

main_path = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
id_path = "/Users/zburchill/Documents/workspace2/python3_files/src/valid_series_ids"
db_file = "first"


########################################################
context("Python")

use_python("/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4", required=TRUE)
sys <- import("sys")

test_that("Using the right Python", {
  expect_equal(sys$version_info$major, 3)
  expect_gte(sys$version_info$minor, 4)
})

source_python(paste0(main_path, "load_for_r.py"))
list_of_dicts <- load_dicts(paste0(main_path, db_file),
                            id_path)

test_that("Loaded SOMETHING from Python file", {
  expect_gte(length(list_of_dicts), 2)
})


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

###################################################################
context("Checking loaded values")

test_that("Broad check of expected number of values", {
  lc <- df.n %>%
    summarize_all(~length(unique(.)))
  
  expect_equal(lc$completely_scanlated, 1)
  expect_equal(lc$was_anime, 1)
  expect_equal(lc$status, 1)
  expect_equal(lc$type, 1)
  
  expect_equal(lc$list_stats, 2)
  expect_equal(lc$user_ratings, 2)
})

test_that("Do `list_stats` have expected values?", {
  
  list_stats <- map(df$data, 
                    ~paste0(sort(names(.$list_stats)), 
                            collapse=";")) %>%
    simplify() %>% factor()
  expect_equal(length(levels(list_stats)), 2)
})



# df2 <- df %>%
#   mutate(x = map(data, ~.$type),
#          y = map(data, ~.$type) %>% simplify() %>% factor())
#          # y = map(data, ~paste0(.$type, collapse=";")) %>% 
#          #   simplify(),
#          # w = map(data, ~paste0(sort(names(.$type)), collapse=";")) %>%
#          #   simplify() %>% factor(),
#          # n = map(data, ~length(.$type)) %>% 
#          #   simplify()) %>%
#   select(-z, -data)
# 
# df2 %>% filter(n > 1) %>% arrange(-n)



