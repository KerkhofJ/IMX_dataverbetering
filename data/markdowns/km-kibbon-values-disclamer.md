# bergeleidend scrhijven km waarden toegevoegd tbv test doeleinden

**⚠️De km-service is geen vrijgegeven tooling maar een open-source project. ProRail neemt in geen geval verantwoordelijkheid voor de resultaten! ⚠️**

- De km waarden zijn niet gecontroleerd en daarom enkel geschikt voor testdoeleinden. De km waarden zijn niet consistent met het OBE-blad!
- Alle objecten die een `GeographicLocation.gml:Point` bevatten, zijn voorzien van een km-waarde.
- Voor het bepalen van de km-waarden is gebruikgemaakt van de open-IMX km-service: [https://github.com/open-imx/kmService](https://github.com/open-imx/kmService)
- De gebruikte data is afkomstig uit de ProRail GIS-data: [https://maps.prorail.nl/arcgis/rest/services/Referentiesysteem/FeatureServer](https://maps.prorail.nl/arcgis/rest/services/Referentiesysteem/FeatureServer) (2025-01-13T15:00:13Z).
- De km-waarden en linten zijn via een script toegevoegd. De toevoegingen zijn XSD-valide, het bestand zelf niet.



### Werking KM-service
- Als een punt in een km-vlak ligt, wordt het gekoppeld aan dat lint. Dit kan leiden tot meerdere km-waarden:
  - Bijvoorbeeld bij kunstwerken.
  - Bij overlappingen van km-vlakken.
- De km-service bepaalt de km-waarde volgens de traditionele (RVT) methode:
  - De laagste raai links of rechts van het punt wordt bepaald.
  - De raai wordt doorgetrokken tot de rand van het km-vlak.
  - De afstand wordt haaks op de laagste raai gemeten.
  - Er wordt niet naar boven of beneden afgerond. Als een punt binnen een meter ligt, krijgt het die meter.
  - Plusmeters worden vanaf 100m weergegeven als `raai_waarde.000` + meters.


### Data-technische aspecten die kunnen leiden tot afwijkingen
- Niet alle hm-punten in de data hebben een eigen raai. Als een hm-punt geen raai heeft, kan dit leiden tot afwijkingen of geen km resultaat.
- De raaien liggen niet op de hm-punten. De service verplaatst de raai naar het hm-punt, wat kan leiden tot afwijkingen ten opzichte van handmatig meten.


## Feedback is welkom via:  
- [GitHub repository van de km-service](https://github.com/open-imx/kmService)  
- [Open-IMX community op Discord](https://discord.gg/wBses7bPFg)  
