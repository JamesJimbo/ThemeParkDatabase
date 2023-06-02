import requests
import sqlite3
import folium
import webbrowser


class Park:
    def __init__(self, name, country, continent, latitude, longitude):
        self.name = name
        self.country = country
        self.continent = continent
        self.latitude = latitude
        self.longitude = longitude


class Company:
    def __init__(self, name):
        self.name = name
        self.parks = []


def createParksTable(cursor):
    cursor.execute('DROP TABLE IF EXISTS parks')
    cursor.execute('''CREATE TABLE parks
                      (name TEXT, country TEXT, continent TEXT, latitude REAL, longitude REAL, company TEXT)''')


def insertParksData(cursor, data):
    for companyData in data:
        companyName = companyData['name']
        for parkData in companyData['parks']:
            parkName = parkData['name']
            parkCountry = parkData['country']
            parkContinent = parkData['continent']
            parkLatitude = parkData['latitude']
            parkLongitude = parkData['longitude']
            cursor.execute("INSERT INTO parks (name, country, continent, latitude, longitude, company) VALUES (?, ?, ?, ?, ?, ?)",
                           (parkName, parkCountry, parkContinent, parkLatitude, parkLongitude, companyName))


def getParksByCountry(cursor):
    cursor.execute("SELECT DISTINCT country FROM parks ORDER BY country")
    countries = cursor.fetchall()

    print("\nAvailable Countries:\n")
    for idx, country in enumerate(countries, start=1):
        print(f"{str(idx).ljust(2)} - {country[0]}")

    selectedCountry = None
    while not selectedCountry:
        selectedCountry = input("\nEnter the number of the country to see parks or press 'q' to go back to the main menu: ")
        if selectedCountry.lower() == 'q':
            return
        try:
            selectedIdx = int(selectedCountry) - 1
            if 0 <= selectedIdx < len(countries):
                selectedCountry = countries[selectedIdx][0]
            else:
                print("Invalid number. Please select a number from the list.")
                selectedCountry = None
        except ValueError:
            print("Invalid input. Please enter a number.")
            selectedCountry = None

    cursor.execute("SELECT name FROM parks WHERE country=? ORDER BY name", (selectedCountry,))
    parkNames = cursor.fetchall()

    print(f"\nParks in {selectedCountry}:\n")
    for park in parkNames:
        print(park[0])
        

    choice = input("\nDo you want to view these parks on a map? (y/n): ")
    if choice.lower() == 'y':
        cursor.execute("SELECT name, latitude, longitude FROM parks WHERE country=? ORDER BY name", (selectedCountry,))
        parks = cursor.fetchall()
        displayParksOnMap(cursor, parks, filter_type="country", filter_value=selectedCountry)


def getParksByContinent(cursor):
    cursor.execute("SELECT DISTINCT continent FROM parks ORDER BY continent")
    continents = cursor.fetchall()

    print("\nAvailable Continents:\n")
    for idx, continent in enumerate(continents, start=1):
        print(f"{idx} - {continent[0]}")

    selectedContinent = None
    while not selectedContinent:
        selectedContinent = input("\nEnter the number of the continent to see parks: ")
        if selectedContinent.lower() == 'q':
            return
        try:
            selectedIdx = int(selectedContinent) - 1
            if 0 <= selectedIdx < len(continents):
                selectedContinent = continents[selectedIdx][0]
            else:
                print("Invalid number. Please select a number from the list.")
                selectedContinent = None
        except ValueError:
            print("Invalid input. Please enter a number.")
            selectedContinent = None

    cursor.execute("SELECT name, country FROM parks WHERE continent=? ORDER BY name", (selectedContinent,))
    parkData = cursor.fetchall()

    print(f"\nParks in {selectedContinent}:\n")
    for park in parkData:
        print(f"Park: {park[0]}\nCountry: {park[1]}\n")

    choice = input("\nDo you want to view these parks on a map? (y/n): ")
    if choice.lower() == 'y':
        cursor.execute("SELECT name, latitude, longitude FROM parks WHERE continent=? ORDER BY name", (selectedContinent,))
        parks = cursor.fetchall()
        displayParksOnMap(cursor, parks, filter_type="continent", filter_value=selectedContinent)


def getParksByCompany(cursor):
    cursor.execute("SELECT DISTINCT company FROM parks ORDER BY company")
    companies = cursor.fetchall()

    print("\nAvailable Companies:\n")
    for idx, company in enumerate(companies, start=1):
        print(f"{str(idx).ljust(2)} - {company[0]}")

    selectedCompany = None
    while not selectedCompany:
        selectedCompany = input("\nEnter the number of the company to see parks: ")
        if selectedCompany.lower() == 'q':
            return
        try:
            selectedIdx = int(selectedCompany) - 1
            if 0 <= selectedIdx < len(companies):
                selectedCompany = companies[selectedIdx][0]
            else:
                print("Invalid number. Please select a number from the list.")
                selectedCompany = None
        except ValueError:
            print("Invalid input. Please enter a number.")
            selectedCompany = None

    cursor.execute("SELECT name, country, continent FROM parks WHERE company=? ORDER BY name", (selectedCompany,))
    parks = cursor.fetchall()

    print(f"\nParks under {selectedCompany}:\n")
    for park in parks:
        print(f"Park Name: {park[0]}\nCountry: {park[1]}\nContinent: {park[2]}\n")

    choice = input("\nDo you want to view these parks on a map? (y/n): ")
    if choice.lower() == 'y':
        cursor.execute("SELECT name, latitude, longitude FROM parks WHERE company=? ORDER BY name", (selectedCompany,))
        parks = cursor.fetchall()
        displayParksOnMap(cursor, parks, filter_type="company", filter_value=selectedCompany)
        

def displayParkCoordinatesOnMap(cursor):
    cursor.execute("SELECT name, latitude, longitude FROM parks ORDER BY name")
    parks = cursor.fetchall()

    print("Available Parks:\n")
    for idx, park in enumerate(parks, start=1):
        print(f"{str(idx).ljust(3)} - {park[0]}")

    selectedPark = None
    while not selectedPark:
        selectedNumber = input("\nSelect a park by number to see coordinates or press 'q' to go back to the main menu: ")
        if selectedNumber.lower() == 'q':
            return

        try:
            index = int(selectedNumber) - 1
            if 0 <= index < len(parks):
                selectedPark = parks[index]
        except ValueError:
            pass

        if not selectedPark:
            print("Invalid number. Please select a number from the list.")

    parkName, latitude, longitude = selectedPark
    print(f"\nPark: {parkName}")
    print(f"Coordinates: ({latitude}, {longitude})")

    # Create a map centered on the park's coordinates
    parkMap = folium.Map(location=[latitude, longitude], zoom_start=12)

    # Add a marker at the park's location
    folium.Marker([latitude, longitude], popup=parkName).add_to(parkMap)

    # Display the map
    mapFilename = "parkMap.html"
    parkMap.save(mapFilename)
    print(f"A map with the park's coordinates has been saved as {mapFilename}.")

    # Open the map in a web browser
    webbrowser.open_new_tab(mapFilename)


def displayParksOnMap(cursor, parks, filter_type=None, filter_value=None):
    filteredParks = []
    if filter_type == "country":
        filteredParks = [(name, lat, lon) for name, lat, lon in parks if cursor.execute("SELECT country FROM parks WHERE name=?", (name,)).fetchone()[0] == filter_value]
    elif filter_type == "company":
        filteredParks = [(name, lat, lon) for name, lat, lon in parks if cursor.execute("SELECT company FROM parks WHERE name=?", (name,)).fetchone()[0] == filter_value]
    elif filter_type == "continent":
        filteredParks = [(name, lat, lon) for name, lat, lon in parks if cursor.execute("SELECT continent FROM parks WHERE name=?", (name,)).fetchone()[0] == filter_value]

    if filteredParks:
        # Create a map centered on the first park's coordinates
        parkMap = folium.Map(location=[filteredParks[0][1], filteredParks[0][2]], zoom_start=12)

        # Add markers for each park
        for park in filteredParks:
            name, lat, lon = park
            folium.Marker(
                location=[lat, lon],
                popup=name
            ).add_to(parkMap)

        # Determine the bounds of the markers
        bounds = [[park[1], park[2]] for park in filteredParks]
        parkMap.fit_bounds(bounds)

        mapFilename = "parkMap.html"
        parkMap.save(mapFilename)
        print(f"A map with the selected parks has been saved as {mapFilename}.")
        webbrowser.open_new_tab(mapFilename)
    else:
        print("No parks found for the selected filter.")


def displayAllParksOnMap(cursor):
    cursor.execute("SELECT name, latitude, longitude FROM parks")
    parks = cursor.fetchall()

    # Create a map
    parkMap = folium.Map(location=[0, 0], zoom_start=2)

    # Add markers for each park
    for park in parks:
        parkName, latitude, longitude = park
        folium.Marker([latitude, longitude], popup=parkName).add_to(parkMap)

    # Display the map
    parkMap.save("allParksMap.html")
    webbrowser.open_new_tab("allParksMap.html")
    

def mainMenu(cursor):
    print("Powered by Queue-Times.com (https://queue-times.com/)")
    while True:
        print("\n-- Main Menu --\n")
        print("1. Display Parks by Country")
        print("2. Display Parks by Company")
        print("3. Display Parks by Continent")
        print("4. Display Park on Map")
        print("5. Display All Parks on Map")
        print("\nPress 'q' to quit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            getParksByCountry(cursor)
        elif choice == "2":
            getParksByCompany(cursor)
        elif choice == "3":
            getParksByContinent(cursor)
        elif choice == "4":
            displayParkCoordinatesOnMap(cursor)
        elif choice == "5":
            displayAllParksOnMap(cursor)
        elif choice.lower() == "q":
            break
        else:
            print("Invalid choice. Please try again.")
            

def main():
    # Connect to the SQLite database
    conn = sqlite3.connect('parkData.db')
    cursor = conn.cursor()

    # Execute the main menu
    createParksTable(cursor)

    response = requests.get("https://queue-times.com/parks.json")
    data = response.json()

    insertParksData(cursor, data)

    mainMenu(cursor)

    # Close the cursor and connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()    
