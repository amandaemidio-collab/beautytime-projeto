// Trims and validates service fields, including the key used for company-level uniqueness.
function "Catalogo/validate_service" {
  input {
    text name filters=trim
    int duration_minutes
    int price_cents
  }

  stack {
    var $normalized_name {
      value = $input.name|trim
    }

    precondition (($normalized_name|strlen) >= 2 && ($normalized_name|strlen) <= 80) {
      error_type = "inputerror"
      error = "service_name_invalid"
    }

    precondition ($input.duration_minutes >= 15 && $input.duration_minutes <= 480 && ($input.duration_minutes|modulus:15) == 0) {
      error_type = "inputerror"
      error = "service_duration_invalid"
    }

    precondition ($input.price_cents >= 0 && $input.price_cents <= 9999999) {
      error_type = "inputerror"
      error = "service_price_invalid"
    }

    var $name_key {
      value = $normalized_name|to_lower
    }
  }

  response = {
    name             : $normalized_name
    name_key         : $name_key
    duration_minutes : $input.duration_minutes
    price_cents      : $input.price_cents
  }
}
