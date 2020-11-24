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

