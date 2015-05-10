create view categories_timeseries_avg as
select name_category,time_bin,avg(sum), shortname_category
from (select time_bin,sum, name_category, shortname_category
      from(select * 
           from (select date_trunc('year', time) time_bin, id_group, SUM(yes_rsvp_count_from_rsvps) 
                 from events group by time_bin, id_group order by id_group, time_bin )t Where t.time_bin is not null) as foo 
      left join 
      (select id_group, name_category, shortname_category from groups) as boo 
      using (id_group)) as koo 
group by name_category, shortname_category, time_bin;
