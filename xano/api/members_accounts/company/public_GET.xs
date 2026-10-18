// Return only public company fields for the booking page.
query "company/public" verb=GET {
  api_group = "Members & Accounts"

  input {
    text public_identifier
  }

  stack {
    db.get account {
      field_name = "public_identifier"
      field_value = $input.public_identifier
      output = ["name", "public_identifier"]
    } as $company
  
    precondition ($company != null) {
      error_type = "notfound"
      error = "Company not found."
    }
  }

  response = {
    name              : $company.name
    public_identifier: $company.public_identifier
  }
  guid = "Q8VuMVUIekYv54eFKiHcdLuc9fw"
}
