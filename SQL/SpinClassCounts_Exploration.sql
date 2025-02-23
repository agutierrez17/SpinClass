SELECT
*
FROM SpinClassCounts
ORDER BY
DATE


----CLASSES PER CLUB
SELECT
CLUB AS Club,
COUNT(*) AS "Number of Classes"
FROM SpinClassCounts

GROUP BY
Club

ORDER BY 
"Number of Classes" DESC;


----CLASSES PER YEAR/MONTH (PER CLUB
SELECT
DATEADD(DAY, 1, EOMONTH(Date, -1)) AS Month,
COUNT(*) AS "Number of Classes"

FROM SpinClassCounts

--WHERE
--Club IN (
----'East Lakeview',
----'Gold Coast',
----'West Loop'
--)

GROUP BY
DATEADD(DAY, 1, EOMONTH(Date, -1))

ORDER BY
"Month";


----RIDERS PER CLUB
SELECT
CLUB AS Club,
SUM(Count) AS "Number of Riders"
FROM SpinClassCounts

GROUP BY
Club

ORDER BY 
"Number of Riders" DESC;


----RIDERS PER YEAR/MONTH
SELECT
DATEADD(DAY, 1, EOMONTH(Date, -1)) AS Month,
SUM(Count) AS "Number of Riders"
FROM SpinClassCounts

GROUP BY
DATEADD(DAY, 1, EOMONTH(Date, -1))

ORDER BY 
"Month";


----AVG RIDERS PER CLASS PER CLUB
SELECT
Club,
ROUND(AVG(Count),0) AS "Average Number of Riders"
FROM SpinClassCounts

WHERE
Class NOT IN ('Intro To Spin')
--AND
--YEAR(Date) = '2024'
--AND
--MONTH(DATE) >= '07'

GROUP BY
Club

ORDER BY 
"Average Number of Riders" DESC;


----AVG RIDERS PER YEAR/MONTH (PER CLUB)
SELECT
DATEADD(DAY, 1, EOMONTH(Date, -1)) AS Month,
ROUND(AVG(Count),0) AS "Average Number of Riders"
FROM SpinClassCounts

WHERE
Class NOT IN ('Intro To Spin')
--AND
--Club IN (
----'East Lakeview',
----'Gold Coast',
----'West Loop'
--)

GROUP BY
DATEADD(DAY, 1, EOMONTH(Date, -1))

ORDER BY 
"Month";





