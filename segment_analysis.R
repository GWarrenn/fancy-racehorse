library(tidyverse)

segment_efforts <- read.csv("segment_effort_results.txt")

segment_efforts$fmt_date <- strptime(segment_efforts$start_date,'%Y-%m-%d %H:%M:%S')

segment_efforts <- segment_efforts %>%
  group_by(activity_id) %>%
  mutate(activity_start_date = max(fmt_date))

## merge in activity-level data to filter out Zwift activities

activities <- read.csv("results.csv") %>%
  filter(activity_type == "Ride") %>%
  rename(activity_id = id) %>%
  select(activity_id)

segment_efforts <- merge(segment_efforts,activities)

activities <- unique(segment_efforts$activity_id)
  
all_records <- data.frame()

for(activity in activities){

  activity_date <- segment_efforts %>%
    filter(activity_id == activity) %>%
    select(activity_start_date) %>%
    distinct() %>%
    top_n(1)
    
  activity_date <- head(activity_date$activity_start_date,1)
  
  previous_segments <- segment_efforts %>%
    filter(activity_start_date < activity_date) %>%
    ungroup() %>%
    select(segment_id) %>%
    distinct() %>%
    mutate(previous_segment = 1)
  
  current_segment <- segment_efforts %>%
    filter(activity_id == activity) %>%
    select(activity_id,segment_id) %>%
    distinct() 
  
  new_segment_check <- merge(current_segment,previous_segments,all.x=T)
  
  new_segment_check <- new_segment_check %>%
    mutate(previous_segment = if_else(new_segment_check$previous_segment == 1,1,0)) %>%
    group_by(activity_id,previous_segment) %>%
    summarise(n=n()) %>%
    mutate(percent = n/sum(n),
           total = sum(n))
  
  new_segment_check$date <- activity_date
  
  all_records <- rbind(new_segment_check,all_records)

}

all_records$legend <- ifelse(is.na(all_records$previous_segment),"New Segment","Old Segment")

all_records_filtered <- all_records %>%
  filter(total >= 10)

all_records_filtered <- as.data.frame(all_records_filtered)

mv_avg_1 <- all_records_filtered %>%
  filter(legend == "New Segment") %>%
  mutate(moving_avg = rollapply(percent,7,mean,align='right',fill=NA)) %>%
  select(activity_id,legend,moving_avg)

mv_avg_2 <- all_records_filtered %>%
  filter(legend == "Old Segment") %>%
  mutate(moving_avg = rollapply(percent,7,mean,align='right',fill=NA)) %>%
  select(activity_id,legend,moving_avg)

mv_avg <- rbind(mv_avg_1,mv_avg_2)

all_records_filtered <- merge(all_records_filtered,mv_avg,all.x=T)

ggplot(all_records_filtered,aes(x=as.Date(date),y=moving_avg,color=legend)) +
  geom_line(size=1) +
  geom_point(data=all_records_filtered,
             aes(x=as.Date(date),y=percent,color=legend),alpha=.5) +
  labs(y="Percent New/Old Segments",
       title="Spice is the variety of life", 
       subtitle = "Percent of segments ridden that are new/old",
       caption="New segments are defined as not having been ridden prior to the given ride",
       color="Legend") +
  theme_bw() +
  theme(legend.position = "bottom",
        axis.title.x=element_blank()) +
  scale_x_date(date_breaks = "2 months",
               date_minor_breaks = "1 month",
               date_labels = "%b")

############################################################
##
## Distribution Plot
##
############################################################

crime_df$month <- as.numeric(format(as.Date(crime_df$REPORT_DAT,"%Y-%m-%d"), "%m"))
crime_df$Year <- format(as.Date(crime_df$REPORT_DAT,"%Y-%m-%d"), "%Y")

yearly_comparison <- all_records_filtered %>%
  filter(legend == "New Segment") %>%
  mutate(year_month = format(as.Date(date,"%Y-%m-%d"), "%Y-%m"),
         year = as.numeric(format(as.Date(date,"%Y-%m-%d"), "%Y"))) 

ggplot(yearly_comparison,aes(x=percent,fill=as.character(year))) +
  geom_density(alpha=.5) +
  labs(y="Density",
       title="Spice is the variety of life", 
       subtitle = "Distribution of percentage of new segments on rides",
       caption="New segments are defined as not having been ridden prior to the given ride",
       color="Legend") +
  theme_bw() +
  theme(legend.position = "bottom",
        axis.title.x=element_blank())

############################################################
##
## Average YoY Monthly New Segments
##
############################################################

monthly_comparison <- yearly_comparison %>%
  group_by(year_month) %>%
  summarise(total_rides = n(),
            avg_new_segments = mean(percent)) %>%
  mutate(fmt_date = as.Date(paste(year_month,"-01",sep="")),
         year = format(fmt_date, "%Y"),
         month = format(fmt_date, "%m"))

ggplot(filter(monthly_comparison,fmt_date >= as.Date("2019-04-01","%Y-%m-%d")),
       aes(x=month,y=avg_new_segments,color=year,group=year)) +
  geom_line(size=1) +
  geom_line(data=filter(monthly_comparison,fmt_date <= as.Date("2019-04-01","%Y-%m-%d")),
            aes(x=month,y=avg_new_segments,color=year,group=year),linetype = "dashed",size=1) +
  labs(y="Average New Segements",
       title="xx", 
       caption="xx",
       color="Legend") +
  theme_bw() +
  scale_color_manual(values = c("#e63c3c","#808080","#2f2fed")) +
  theme(legend.position = "bottom",
        axis.title.x=element_blank())

############################################################
##
## Distance by % new segments
##
############################################################

activities <- read.csv("results.csv") %>%
  filter(activity_type == "Ride") %>%
  rename(activity_id = id) %>%
  select(activity_id,distance)

distance_newness <- merge(all_records_filtered,activities) %>%
  filter(legend == "New Segment") %>%
  mutate(year_month = format(as.Date(date,"%Y-%m-%d"), "%Y-%m"),
         fmt_date = as.Date(paste(year_month,"-01",sep="")),
         year = format(fmt_date, "%Y"),
         month = format(fmt_date, "%m"))

ggplot(distance_newness,aes(x=distance,y=percent,color=year)) +
  geom_point() +
  geom_hline(data = distance_newness,
             aes(yintercept = mean(percent))) +
  geom_vline(data = distance_newness,
             aes(xintercept = mean(distance)))


############################################################
##
## Distribution of total segment attempts
##
############################################################

segment_efforts <- segment_efforts %>%
  arrange(segment_id,activity_start_date) %>%
  group_by(segment_id) %>%
  mutate(hours = as.numeric(str_extract(moving_time, "^[0-9]?[0-9]")),
         mins = as.numeric(gsub(x = str_extract(moving_time, ":[0-9][0-9]:"),pattern = ":",replacement = "")),
         secs = as.numeric(str_extract(moving_time, "[0-9][0-9]$")),
         total_time_secs = (hours * 3600) + (mins * 60) + secs, 
         num_attempts = sum(n()),
         attempt_number = n())

all_effort_numbers_dist <- ggplot(segment_efforts,aes(num_attempts)) +
  geom_histogram(aes(y=..density..), colour="black", fill="white") +
  geom_density(alpha=.2, fill="#FF6666") +
  geom_vline(xintercept = median(segment_efforts$num_attempts))

activities <- read.csv("results.csv") %>%
  filter(activity_type == "Ride") %>%
  rename(activity_id = id) %>%
  select(activity_id,commute)

segment_efforts <- merge(segment_efforts,activities)

commute_effort_numbers_dist <- ggplot(segment_efforts,aes(num_attempts)) +
  geom_histogram(aes(y=..density..), colour="black", fill="white")+
  geom_density(alpha=.2, fill="#FF6666") +
  facet_wrap(~commute)

############################################################
##
## Segment effort times
##
############################################################

segment_effort_times <- segment_efforts %>%
  filter(commute == "False") %>%
  group_by(segment_id) %>%
  mutate(num_attempts = n(),
         attempt_num = row_number()) %>%
  filter(num_attempts >= 10) %>%
  ungroup() %>%
  mutate(total_attempts_quartile = ntile(num_attempts,4)) %>%
  arrange(segment_id,attempt_num) %>%
  group_by(segment_id) %>%
  mutate(decile = ntile(attempt_num, 10)) %>%
  group_by(total_attempts_quartile,decile) %>%
  summarise(avg_time = mean(total_time_secs),
            n = sum(n()))

ggplot(segment_effort_times,aes(x=decile,y=avg_time)) +
  geom_bar(stat="identity") +
  geom_smooth(method = "lm") +
  facet_wrap(~total_attempts_quartile)

regression_df <- segment_efforts %>%
  filter(commute == "False") %>%
  group_by(segment_id) %>%
  mutate(num_attempts = n(),
         attempt_num = row_number()) %>%
  filter(num_attempts >= 10) %>%
  ungroup() %>%
  mutate(total_attempts_quartile = ntile(num_attempts,4)) %>%
  arrange(segment_id,attempt_num) %>%
  group_by(segment_id) %>%
  arrange(segment_id,attempt_number) %>%
  group_by(segment_id) %>%
  mutate(decile = ntile(attempt_number, 10),
         distance_meters = as.numeric(gsub(x = distance,pattern = " m",replacement = "")))


summary(lm(regression_df,formula = total_time_secs ~ distance_meters + total_attempts_quartile + decile))


