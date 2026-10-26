// Returns true when the professional already has a period on that day overlapping the given interval.
// Periods that only touch (one ends exactly when the other starts) do not overlap.
function "Agenda/find_hours_overlap" {
  input {
    int professional_id
    int day_of_week
    int start_minute
    int end_minute
    int? exclude_hour_id?=null
  }

  stack {
    db.query professional_hours {
      where = $db.professional_hours.professional_id == $input.professional_id && $db.professional_hours.day_of_week == $input.day_of_week && $db.professional_hours.start_minute < $input.end_minute && $db.professional_hours.end_minute > $input.start_minute && ($input.exclude_hour_id == null || $db.professional_hours.id != $input.exclude_hour_id)
      return = {type: "exists"}
    } as $has_overlap
  }

  response = $has_overlap
  guid = "1jsTr_mpx3jcu5uU-M2ZYSShvnw"
}
