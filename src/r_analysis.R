library(jsonlite)
library(dplyr)
library(magrittr)
library(purrr)
# ya need this one
stopifnot(rlang::is_installed("lubridate"))

# to-do: 
#   weirdos for statuses like 1110

#   give forum_stuff names: "topics", and "posts"

#   check in the issues if there's a oneshot (or "one-shot" or variants), and whether that agrees with the status

#   also check and see if there's more than one chapter

#   technically, you should be able to save multiple oneshots, e.g., 54639, but i think you just save the last one

#   should probably use ids for EVERYTHING (artists, publications, etc)

#   remove extra strings (in Python):
#     31891, serialized_in: "Comic Gum"    "(Wani Books)" "" 
#     54639: category_recs: ""Working Woman"  ""
#
#   strip text:
# 59572:
      # $regulars
      # [,1]        [,2]        
      # [1,] "1 Volume " "(Complete)"

# maybe check if an author is "anthology" and filter it out



######################################
############# Functions
########################################

is_oneshot <- function(x) {
  grepl("one[- ]*shot", tolower(x))
}


df_rower <- function(x,name) {
  name <- rlang::enquo(name)
  tibble::as_tibble(rlang::list2(!! rlang::quo_name(name) := rlang::list2(x)))
}

filter_by_row <- function(.data, ...) {
  if (is.grouped_df(.data))
    stop("Filtering by row would remove grouping!")
  .data %>% rowwise() %>% filter(...) %>% ungroup()
}

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

#########################

main_path = "/Users/zburchill/Documents/workspace2/web-scraping/src/"
metadata_db_file = "everything_json.json"
# issue_db_file = "first_1891_issues"

metadata_list <- fromJSON(paste0(main_path, metadata_db_file), flatten=FALSE)




# Turns the issues list into a data frame
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




#################################### DAyum

# year, completely_scanlated, licensed, was_anime, type, last_updated
# forum stuff should have two: "topics" and then "posts"
#
# status should either be length of 2, in which case you want to check 
#     to see if the second thing is a oneshot (almost definitely is), 
#     and if so, make a column called oneshot status
#   If it's length 1, check if there is any non-"complete" values in the second column. If there is, give the "continuing" status what it needs
# l %>% keep(~("regulars" %in% names(.$status))) %>% purrr::map(~.$status$regulars[,2]) %>% purrr::flatten() %>% unique()
# or: l %>% keep(~("regulars" %in% names(.$status)))%>% purrr::map(~.$status$regulars[,2]) %>% purrr::flatten() %>% gsub("[[:punct:]]", "", .) %>% as_vector() %>% paste0(collapse=" ") %>% write(file="~/Desktop/delete.txt")

manga_is_ended <- "drop|finish|discontin|complete|axed|death|cancel"
manga_ongoing  <- "ongoing"
manga_not_done <- "ongoing|hiatus"
unknown <- "\\?|N\\/A"

# "ongoing" "complete" "reprint" "hiatus" "incomplete" "?"
# "dropped" "discontinued" "Finished" "Cancelled" "death" "Canceled"
# "Complete/Discontinued" "Compete" "Axed" "passed away" "Unfinished"
# what's up with ""?
# deal with: e.g. 149294
# [,1]  [,2]
# [1,] "N/A" ""  
# or: 48442

clean_metadata <- function(df) {
  single_value_colnames <- c("year", "completely_scanlated", "licensed", "was_anime", "type", "last_updated")
  
  df %>% 
    rowwise() %>%
    # Take care of the single-value columns
    mutate_at(single_value_colnames,
              ~ifelse(is.null(.), NA, .)) %>% ungroup() %>%
    # Take care of the forum topic stuff
    mutate(ForumNumTopics = forum_stuff[1],
           ForumNumPosts = forum_stuff[2]) %>%
    # Turn the date into a date, but there's gonna be null vals
    mutate(last_updated = suppressWarnings(
      lubridate::mdy_hm(last_updated, tz="America/Los_Angeles"))) %>%
    ungroup() %>%
    # Make the dates right
    # remove type and forum_stuff because they're redundant
    select(-type, -forum_stuff)
}


make_single_series_dataframe <- function(series, series_id) {
  df <- series %>% 
    purrr::map(function(v) {
      if (length(v) == 0) NULL
      else if (length(v) == 1 && trimws(v) == "N/A") NULL
      else  v }) %>%
    purrr::imap_dfc(~df_rower(.x, !! .y)) 
  if (is.null(df$categories[[1]])) {
    # If there are no categories, the recs should have "N/A"
    stopifnot(length(df$category_recs[[1]]) == 1 &&
                grepl("N/A", df$category_recs[[1]]))
    df$category_recs <- NULL
  }
  df %>% mutate(SeriesID = series_id)
}



make_metadata_dataframe <- function(l) {
  len <- length(l)
  # Remove anything that isn't just a oneshot
  l <- l %>% keep(~!("regulars" %in% names(.$status)))
  message(paste0("Removed ", len-length(l), " oneshot series"))
  
  len2 <- length(l)
  # Remove anything related to Anthologies
  l %>% purrr::keep(~!("Anthology" %in% .$artists) &
                 !("Anthology" %in% .$authors)) %>%
    purrr::imap_dfr(function(series, series_id) {
      tibble(SeriesID = series_id,
             data = list(series)) })
  message(paste0("Removed ", len2-nrow(df), " anthology series"))
}

md_df <-make_metadata_dataframe(metadata_list)
df.n <- md_df %>%
  bind_cols(map_df(.$data, ~map(., length))) %>%
  select(-data)

# View a summary of the lengths
library(summarytools)
view(dfSummary(df.n))

# User_ratings should have 2 lengths
# Check for "Anthology" in artists and authors
# list_stats should have two (can't have 'completed' an unfinished work)

# 







########################################################


df.n %>%
  summarize_all(~length(unique(.))) %>%
  as.data.frame()


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


