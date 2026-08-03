{% test no_duplicate_channel_inside_channels(model) %}

select
    campaign_id,
    channels
from {{ model }}
where channels is not null
  and array_length(channels) != (
        select count(distinct channel)
        from unnest(channels) as channel
    )

{% endtest %}
