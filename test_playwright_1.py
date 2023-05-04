import re
import pytest
from datetime import datetime, timedelta


def test(page):
    filter_items = []

    # Define locators
    GENERAL_MODALS_COOKIE_POPUP_ACCEPT = "(//section[@id='cookie_consent']//button)[last()]"
    FILTERING_FILTER_OPTION_LABELS = "//div[contains(@data-test, 'Header-transport')]//div[contains(@class, 'ChoiceGroup')]//label"
    FILTERING_FILTER_TEXT_WRAP = "xpath=.//span[contains(@class, 'Checkbox')][contains(@class, 'LabelText')]"
    FILTERING_FILTER_CHECKBOX_LABEL = "//div[contains(@data-test, 'Header-transport')]//div[contains(@class, 'Stack')]/*[contains(@class, 'FilterWrapper') or contains(@class, 'Checkbox')][descendant::*[contains(text(), '{item_text}')]]"
    FILTERING_FILTER_CHECKBOX = "xpath=.//div[contains(@class, 'Checkbox')]"
    FLIGHT_CARDS = "//div[contains(@class, 'ResultCardInner')]"
    SEARCH_ITINERARY_DETAILS_TRANSPORT_ICON = "xpath=.//div[contains(@data-test, 'TripTypeBadge')]"
    SEARCH_ORIGIN_FIELD = "//div[contains(@data-test, 'SearchPlaceField-origin')]"
    SEARCH_INPUT = "xpath=.//input[@data-test='SearchField-input']"
    SEARCH_REMOVE_BUTTON = "xpath=.//div[@data-test='PlacePickerInputPlace-close']"
    SEARCH_FROM_TO_SELECTION = (
        "(//div[contains(@data-test, 'PlacePickerRow-{place_type}')])[1]//*[contains(text(), '{city}')]"
    )
    SEARCH_DESTINATION_FIELD = "//div[contains(@data-test, 'SearchPlaceField-destination')]"
    SEARCH_DATE_PICKER_BUTTON = (
        "(//div[@data-test='SearchDateInput']//input[contains(@name,'search-{date_type}')])[{index}]"
    )
    SEARCH_DATE_PICKER_SELECT_DATE = "//div[@data-type='DayContainer'][contains(@data-value, '{flight_date}')]"
    SEARCH_BUTTON = "//*[contains(@data-test, 'SearchButton') or contains(@data-test, 'searchMultiCity') or contains(@class, 'SearchButton') or contains(@class, 'NomadFormFindRoutes')]"
    DATE_PICKER_DONE_BUTTON = "//button[@data-test='SearchFormDoneButton']"
    SEARCH_CHECK_BOOKING_ACCOMMODATION = "//div[contains(@class, 'BookingcomSwitch')]//label"
    SEARCH_FLIGHT_TYPE_BUTTON = "//div[contains(@data-test, 'SearchFormModesPicker')]"
    SEARCH_FLIGHT_TYPE_SELECTION = "//*[@data-test='ModePopupOption-{flight_type}']"
    GENERAL_LOADERS_LOADING_LINE = "//div[contains(@class, 'MapLoaders') or contains(@data-test, 'ResultList')]//div[contains(@class, 'LoadingLinestyled__LoadingLineWrapper')]"

    # Close cookie modal
    page.get_element(GENERAL_MODALS_COOKIE_POPUP_ACCEPT).click()
    page.wait_loading(GENERAL_LOADERS_LOADING_LINE, time_to_appear=5, time_to_disappear=15)

    page.page_pause()

    # Select flight type
    page.get_element(SEARCH_FLIGHT_TYPE_BUTTON).click()
    page.get_element(SEARCH_FLIGHT_TYPE_SELECTION.format(flight_type="oneWay")).click()

    # Select origin
    origin_field = page.get_elements(SEARCH_ORIGIN_FIELD)[0]
    origin_field.get_element(SEARCH_REMOVE_BUTTON).click()
    origin_field.get_element(SEARCH_INPUT).click()
    origin_field.get_element(SEARCH_INPUT).send_keys("Prague")
    # Select first place
    page.get_element(SEARCH_FROM_TO_SELECTION.format(place_type="city", city="Prague")).click()

    # Select destination
    destination_field = page.get_elements(SEARCH_DESTINATION_FIELD)[0]
    destination_field.get_element(SEARCH_INPUT).click()
    destination_field.get_element(SEARCH_INPUT).send_keys("Brno")
    # Select first place
    page.get_element(SEARCH_FROM_TO_SELECTION.format(place_type="city", city="Brno")).click()

    # Select date
    calendar_xpath = SEARCH_DATE_PICKER_BUTTON.format(date_type="outboundDate", index=1)
    date_range_delta = [5, 7]
    date_from = datetime.now() + timedelta(days=date_range_delta[0])
    date_to = datetime.now() + timedelta(days=date_range_delta[1])
    page.get_element(calendar_xpath).click()

    date_from_xpath = SEARCH_DATE_PICKER_SELECT_DATE.format(flight_date=datetime.strftime(date_from, "%m-%d"))
    date_from_element = page.get_element(date_from_xpath)
    date_to_xpath = SEARCH_DATE_PICKER_SELECT_DATE.format(flight_date=datetime.strftime(date_to, "%m-%d"))
    date_to_element = page.get_element(date_to_xpath)

    # Select travel dates (date range)
    date_from_element.hover()
    page.mouse.down()
    date_to_element.hover()
    page.mouse.up()

    # Close date picker modal
    page.get_element(DATE_PICKER_DONE_BUTTON).click()

    # Uncheck 'Check accommodation..' button
    checkbox = page.get_element(SEARCH_CHECK_BOOKING_ACCOMMODATION)
    checkbox_input = checkbox.get_element("xpath=.//input")
    if checkbox_input.is_checked():
        checkbox.click()

    # Press 'Search' button
    page.get_element(SEARCH_BUTTON).click()

    # Get all filter options
    filter_options = page.get_elements(FILTERING_FILTER_OPTION_LABELS)
    for option in filter_options:
        option_text = str(option.get_element(FILTERING_FILTER_TEXT_WRAP, state="attached").text())
        option_text = option_text.replace("\n", "")
        option_text = option_text.replace("only", "")
        option_text = option_text.replace("Only", "")

        filter_items.append(option_text)

    # Deselect all transport filter labels (just for case, sometimes some of them can be checked)
    for item in filter_items:
        item_xpath = FILTERING_FILTER_CHECKBOX_LABEL.format(item_text=item)
        item = page.get_element(item_xpath)

        if item.get_element("xpath=.//input", state="attached").is_checked():
            item.get_element(FILTERING_FILTER_CHECKBOX, state="visible").click()

    wait_results(page)

    # Apply 'Flight' and 'Train'
    for selection in ["Flight", "Train"]:
        label_xpath = FILTERING_FILTER_CHECKBOX_LABEL.format(item_text=selection)
        label = page.get_element(label_xpath)

        label.click()

    wait_results(page)

    # Scroll down , a bit up and full up to render results (page rendering works in this way)
    scroll_px = -200
    height = page.evaluate("document.body.scrollHeight")
    page.evaluate(f"window.scrollTo(0, {height})")
    page.evaluate(f"window.scrollBy(0, {scroll_px});")
    page.evaluate("window.scrollTo(0, 0)")

    # Get all flights
    flights = page.get_elements(FLIGHT_CARDS)

    # For each flight validate right filter(Flight, Train) is applied
    for flight in flights:
        transport_icon_data = flight.get_element(SEARCH_ITINERARY_DETAILS_TRANSPORT_ICON).get_attribute(
            "data-test"
        )
        transports = [transport for transport in transport_icon_data.split("-") if transport.islower()]

        for transport in transports:
            if transport not in ["flight", "train"]:
                pytest.fail(f"Error, wrong transport type, {transport}")

    # Validate each journey matches search details i.e. origin, destination and dates
    search_details = [{'origin': 'Prague', 'destination': 'Brno', 'flight_date': {'from': date_from.date(), 'to': date_to.date()}}]

    flights = page.get_elements(FLIGHT_CARDS)

    for flight in flights:
        i = 0

        journey_details = get_journey_details(flight)

        if len(search_details) != len(journey_details):
            pytest.fail("Number of journey segments({len(journey_details)}) is incorrect")

        for detail in journey_details:
            # Validate "origin" & "destination"
            origin = re.sub(r"[^\s\w\.,]", "", search_details[i].get("origin"))
            destination = re.sub(r"[^\s\w\.,]", "", search_details[i].get("destination"))

            if origin not in detail.get("flight_path"):
                pytest.fail(f"\"{origin}\" not in \"{detail.get('flight_path')}\"")

            if destination not in detail.get("flight_path"):
                pytest.fail(f"\"{destination}\" not in \"{detail.get('flight_path')}\"")

            # Validate "departure date"
            # flight_date can be set of datetime.date values or int ("Time of stay") values
            flight_date = search_details[i].get("flight_date")
            date_from = flight_date.get("from") or flight_date.get("days_in_destination_from")
            date_to = flight_date.get("to") or flight_date.get("days_in_destination_to")

            # Check if departure dates are actually "Time of stay"
            if isinstance(date_from, int):
                arrival_date = journey_details[i - 1].get("arrival_time").date()

                # Calculate valid departure date range base on previous segment arrival date and "days in destination"
                date_from = arrival_date + timedelta(days=date_from)
                date_to = arrival_date + timedelta(days=date_to)

            departure_date = detail.get("departure_time").date()

            if not (date_from <= departure_date <= date_to):
                pytest.fail(f"departure date ({departure_date}) not in range {date_from} - {date_to}")

            i += 1


def get_journey_details(journey):
    # Define locators
    SEARCH_JOURNEY_FLIGHT_SECTION = "xpath=.//div[contains(@class, 'ResultCardSection')][descendant::time]"
    SEARCH_JOURNEY_FLIGHT_DEPARTURE_TIME = "xpath=(.//strong//time)[1]"
    SEARCH_JOURNEY_FLIGHT_ARRIVAL_TIME = "xpath=(.//strong//time)[2]"
    SEARCH_JOURNEY_FLIGHT_ORIGIN = "xpath=.//div[1]//span[contains(@class, 'Place-')]"
    SEARCH_JOURNEY_FLIGHT_ORIGIN_STATION = "xpath=.//div[1]//*[contains(@class, 'PlaceDetails-')]"
    SEARCH_JOURNEY_FLIGHT_DESTINATION = "xpath=.//div[3]//span[contains(@class, 'Place-')]"
    SEARCH_JOURNEY_FLIGHT_DESTINATION_STATION = "xpath=.//div[3]//*[contains(@class, 'PlaceDetails-')]"

    details = list()

    # For each section get departure and arrival dates, origin and destination
    for flight in journey.get_elements(SEARCH_JOURNEY_FLIGHT_SECTION, state="attached"):
        # Departure time
        departure_time_element = flight.get_element(SEARCH_JOURNEY_FLIGHT_DEPARTURE_TIME, state="attached")
        departure_time_string = departure_time_element.get_attribute("datetime")

        dep_date_time_string = departure_time_string.replace("T", " ")
        dep_date_time_string = re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", dep_date_time_string).group(0)  # e.g. match 2020-09-11 15:40:00
        departure_time = datetime.strptime(dep_date_time_string, "%Y-%m-%d %H:%M:%S")

        # Arrival time
        arrival_time_element = flight.get_element(SEARCH_JOURNEY_FLIGHT_ARRIVAL_TIME, state="attached")
        arrival_time_string = arrival_time_element.get_attribute("datetime")

        arr_date_time_string = arrival_time_string.replace("T", " ")
        arr_date_time_string = re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", arr_date_time_string).group(
            0)  # e.g. match 2020-09-11 15:40:00
        arrival_time = datetime.strptime(arr_date_time_string, "%Y-%m-%d %H:%M:%S")

        # Origin and destination
        origin = flight.get_element(SEARCH_JOURNEY_FLIGHT_ORIGIN, state="attached").text()
        origin_station = flight.get_element(SEARCH_JOURNEY_FLIGHT_ORIGIN_STATION, state="attached").text()
        destination = flight.get_element(SEARCH_JOURNEY_FLIGHT_DESTINATION, state="attached").text()
        destination_station = flight.get_element(SEARCH_JOURNEY_FLIGHT_DESTINATION_STATION, state="attached").text()
        flight_path = f"{origin}, {origin_station} - {destination}, {destination_station}".replace("\n", "")

        # Append and return
        details.append({"flight_path": flight_path, "departure_time": departure_time, "arrival_time": arrival_time})

    return details


def wait_results(page):
    # Define locators
    GENERAL_LOADERS_RESULT_LIST_SPINNER = (
        "//div[contains(@class, 'SearchView')]/div[contains(@class, 'Loading__StyledLoading')]"
    )
    GENERAL_LOADERS_OVERLAY = "//div[contains(@class, 'LoadingOverlay')]//div[contains(@class, 'placeholdersWrapper')]"
    GENERAL_LOADERS_LOADING_LINE = "//div[contains(@class, 'MapLoaders') or contains(@data-test, 'ResultList')]//div[contains(@class, 'LoadingLinestyled__LoadingLineWrapper')]"
    SEARCH_NO_RESULT = "//div[contains(@class, 'NoResults') or contains(text(), 'No results')]"
    SEARCH_NO_RESULT_ERROR = "//*[contains(text(), 'having some issues')]"

    # Wait for loading
    page.wait_loading(GENERAL_LOADERS_RESULT_LIST_SPINNER, time_to_appear=1, time_to_disappear=5)
    page.wait_loading(GENERAL_LOADERS_OVERLAY, time_to_appear=2, time_to_disappear=5)
    page.wait_loading(GENERAL_LOADERS_LOADING_LINE, time_to_appear=5, time_to_disappear=30)

    # Set message and fail if no results
    if page.if_exists(SEARCH_NO_RESULT):
        msg = "Flight not found"
        pytest.fail(msg)
    elif page.if_exists(SEARCH_NO_RESULT_ERROR):
        msg = "Sorry we're having some issues. Try reloading the page"
        pytest.fail(msg)
    else:
        pass

