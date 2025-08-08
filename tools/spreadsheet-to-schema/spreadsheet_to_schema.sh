#!/bin/bash
#
# Requirements:
# - https://duckdb.org/
# - https://jqlang.github.io/jq/

SPREADSHEET="Data cluster matrices_20231004.xlsx"
WORKSHEET="Struttura_catalogue"
SCHEMA="struttura.json"

HELP_POSITION="top"
HELP_ALLOW_HTML="true"

set -euo pipefail

echo "# Conversion report"
echo "## Entries processed"

OGR_XLSX_HEADERS=FORCE duckdb << EOF | jq -s '{dataset_fields: del(.[][] | nulls)}' > "$SCHEMA"
install spatial;
load spatial;
load json;
create macro labelize(str) as trim(regexp_replace(lcase(str), '[^a-z0-9]+', '-', 'g'), '-');
copy (
select case when any_value(start_form_page_title) is not null then
       json_object(
          'title', any_value(start_form_page_title),
          'description', any_value(start_form_page_description)
       )
       else null
       end as start_form_page,
       labelize(field_name) as field_name,
       any_value(field_label) as label,
       case when any_value(cluster) is not null then
         labelize(any_value(cluster))
       else null
       end as cluster,
       case when field_type in ('multiple_checkbox', 'radio')
            then field_type
       end as preset,
       case when field_type in ('multiple_checkbox', 'radio') then
       json_group_array(
         json_object(
           'value', labelize(label),
           'label', label
         )
       )
       else null
       end as choices,
       any_value(help_text) as help_text,
       case when any_value(help_text) is not null then
         '$HELP_POSITION'
       else null
       end as help_position,
       case when any_value(help_text) is not null then
         $HELP_ALLOW_HTML == 'true'
       else null
       end as help_allow_html
  from st_read('$SPREADSHEET', layer='$WORKSHEET')
 where field_type in ('multiple_checkbox', 'radio', 'text')
 group by field_name, field_type
) to '/dev/stdout' (format json);
EOF

echo -n "Entries processed: "

OGR_XLSX_HEADERS=FORCE duckdb << EOF 2>/dev/null
install spatial;
load spatial;
load json;
.headers off
.mode ascii
select count(*)
  from st_read('$SPREADSHEET', layer='$WORKSHEET')
 where field_type in ('multiple_checkbox', 'radio', 'text')
EOF
echo

echo "## Entries not processed"
echo "### field_type not supported"

OGR_XLSX_HEADERS=FORCE duckdb << EOF
install spatial;
load spatial;
load json;
.mode markdown
select *
  from st_read('$SPREADSHEET', layer='$WORKSHEET')
 where field_type not in ('multiple_checkbox', 'radio', 'text')
EOF
