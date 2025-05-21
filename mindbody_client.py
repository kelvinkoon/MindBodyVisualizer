import csv

import requests

from constants import MAX_PAGE_SIZE, SIGNED_IN_STR


class Booking:
    def __init__(self, class_name, class_location, instructor, start_time):
        self.class_name = class_name
        self.class_location = class_location
        self.instructor = instructor
        self.start_time = start_time

class MindBodyClient:
    def __init__(self):
        self.bearer_auth_token = self.getAuthToken("creds/auth_token.txt")
        self.studio_allow_list = self.getStudioAllowList("allow_lists/dance_studios.txt")
        self.base_url = "https://prod-mkt-gateway.mindbody.io/v1"
        self.output_path = "output/classes.csv"

    def getAuthToken(self, file_path):
        f = open(file_path)
        bearer_auth_token = f.read()
        # TODO: Ensure bearer token exists and log if not, try-catch
        return bearer_auth_token

    def getStudioAllowList(self, file_path):
        f = open(file_path)
        allow_list_studios_csv = f.read()
        allow_list_studios_arr = allow_list_studios_csv.split(",")
        allow_list_studios = {}
        for studio in allow_list_studios_arr:
            allow_list_studios[studio.strip().lower()] = True
        # TODO: Log allow listed studios 
        return allow_list_studios

    def isSignedIn(self, booking):
        if not booking["attributes"]["status"]:
            return False
        return True if booking["attributes"]["status"][0]["title"] == SIGNED_IN_STR else False
    
    def isInAllowList(self, booking):
        return True if booking["attributes"]["locationName"].strip().lower() in self.studio_allow_list else False

    def getHeaders(self, bearer_auth_token):
        headers = {
            'accept': 'application/vnd.api+json',
            'accept-language': 'en-US,en;q=0.6',
            'authorization': bearer_auth_token,
            'origin': 'https://www.mindbodyonline.com',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'x-mb-app-build': '2025-05-15T11:50:38.730Z',
            'x-mb-app-name': 'mindbody.io',
            'x-mb-app-version': '2b4c248a',
            'x-mb-user-session-id': 'oeu1747807977983r0.7148963000129424',
        }
        return headers

    def getParams(self):
        params = {
            'filter.ascending': 'true',
            # 'filter.include_appointments': 'true',
            # 'filter.include_waitlist': 'true',
            'filter.include_classes': 'true',
            'page.size': MAX_PAGE_SIZE,
        }
        return params

    def getBookings(self):
        headers = self.getHeaders(self.bearer_auth_token)
        params = self.getParams()

        endpoint = "/user/bookings"
        bookings = []
        while endpoint:
            response = requests.get(self.base_url + endpoint, 
                                    params=params, headers=headers)
            # TODO: Try-catch for auth errs
            for booking in response.json()["data"]:
                if self.isInAllowList(booking) and self.isSignedIn(booking):
                    detailed_booking = Booking(
                        booking["attributes"]["name"],
                        booking["attributes"]["locationName"],
                        "N/A" if not booking["attributes"]["serviceStaff"] else booking["attributes"]["serviceStaff"][0]["name"],
                        booking["attributes"]["startTime"],
                    ) 
                    bookings.append(detailed_booking)
                else:
                    print("Skipping booking from '{studio}' for '{start_time}".format(
                        booking["attributes"]["locationName"], ))
            endpoint = response.json()["links"]["next"]

        return bookings

    def saveCsv(self, bookings, path):
        fields = ["class_location", "class_name", "instructor", "start_time"]
        rows = []
        for booking in bookings:
            rows.append([
                booking.class_location,
                booking.class_name,
                booking.instructor,
                booking.start_time
            ])
        
        with open(path, "w") as file:
            csvwriter = csv.writer(file)
            csvwriter.writerow(fields)
            csvwriter.writerows(rows)
            print("CSV saved at '{path}'".format(path=path))

    def createClassCsv(self):
        bookings = self.getBookings()
        self.saveCsv(bookings, self.output_path) 
