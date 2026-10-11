# Enter birth data

Open **Birth Data** from the empty chart screen, or choose **File → New Chart**. To change a chart that is already on screen, choose **Edit Birth Data**.

The dialog is **Enter Birth Data**. Fill it in, then choose **Generate Chart**.

## Name and time

**Name** is the label on the chart.

**Date of Birth** is three numbers: **Day**, **Month**, and **Year**. Month is `1` for January through `12` for December.

**Hour** and **Minute** are the birth time in 24-hour time. Hour `0` is midnight and hour `15` is 3 pm. The time places the houses and the faster planets.

## Place

**Latitude** and **Longitude** are the birth place in decimal degrees. Latitude runs from `-90` to `90`. Longitude runs from `-180` to `180`. The chart is calculated from these numbers.

**City** and **Country** are stored with the chart as place names. They do not look up the coordinates.

**Timezone** can stay empty. The app then fills an IANA name from the latitude and longitude, such as `Australia/Sydney`. You can type a name yourself if you already know it.

## House system

**House System** chooses how the twelve houses are drawn for this chart. **Placidus** is the starting choice. The same list is in [Preferences](preferences.md), and saving preferences there updates this field.

## Generate

Choose **Generate Chart**. The wheel replaces the empty workspace.

The first chart for a century downloads a small Swiss Ephemeris file and stores it on this computer. Later charts for years in that century reuse it. The app works offline after that file is stored.

**Reset** clears the dialog back to an empty chart.
