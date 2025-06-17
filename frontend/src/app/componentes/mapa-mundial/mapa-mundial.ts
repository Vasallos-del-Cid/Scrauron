import { Component, OnInit, Input, OnChanges, SimpleChanges } from '@angular/core';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';
import { FeatureCollection, Geometry, GeoJsonProperties } from 'geojson';
import { Topology } from 'topojson-specification';

@Component({
    selector: 'app-mapa-mundial',
    template: `<div id="mapa-d3" style="display: flex; justify-content: center;"></div>`
})
export class MapaMundialComponent implements OnInit, OnChanges {
    @Input() dataPorPais: Record<string, number> = {};
    private nombreInglesAISO3: Record<string, string> = {
        "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA", "Andorra": "AND",
        "Angola": "AGO", "Antigua and Barbuda": "ATG", "Argentina": "ARG",
        "Armenia": "ARM", "Australia": "AUS", "Austria": "AUT",
        "Azerbaijan": "AZE", "Bahamas": "BHS", "Bahrain": "BHR",
        "Bangladesh": "BGD", "Barbados": "BRB", "Belarus": "BLR",
        "Belgium": "BEL", "Belize": "BLZ", "Benin": "BEN",
        "Bhutan": "BTN", "Bolivia": "BOL", "Bosnia and Herzegovina": "BIH",
        "Botswana": "BWA", "Brazil": "BRA", "Brunei": "BRN",
        "Bulgaria": "BGR", "Burkina Faso": "BFA", "Burundi": "BDI",
        "Cabo Verde": "CPV", "Cambodia": "KHM", "Cameroon": "CMR",
        "Canada": "CAN", "Chad": "TCD", "Chile": "CHL",
        "China": "CHN", "Colombia": "COL", "Comoros": "COM",
        "Congo (Brazzaville)": "COG", "Congo (Kinshasa)": "COD", "Costa Rica": "CRI",
        "Croatia": "HRV", "Cuba": "CUB", "Cyprus": "CYP",
        "Czechia": "CZE", "Denmark": "DNK", "Djibouti": "DJI",
        "Dominica": "DMA", "Dominican Republic": "DOM", "Ecuador": "ECU",
        "Egypt": "EGY", "El Salvador": "SLV", "Equatorial Guinea": "GNQ",
        "Eritrea": "ERI", "Estonia": "EST", "Eswatini": "SWZ",
        "Ethiopia": "ETH", "Fiji": "FJI", "Finland": "FIN",
        "France": "FRA", "Gabon": "GAB", "Gambia": "GMB",
        "Georgia": "GEO", "Germany": "DEU", "Ghana": "GHA",
        "Greece": "GRC", "Grenada": "GRD", "Guatemala": "GTM",
        "Guinea": "GIN", "Guinea-Bissau": "GNB", "Guyana": "GUY",
        "Haiti": "HTI", "Honduras": "HND", "Hungary": "HUN",
        "Iceland": "ISL", "India": "IND", "Indonesia": "IDN",
        "Iran": "IRN", "Iraq": "IRQ", "Ireland": "IRL",
        "Israel": "ISR", "Italy": "ITA", "Jamaica": "JAM",
        "Japan": "JPN", "Jordan": "JOR", "Kazakhstan": "KAZ",
        "Kenya": "KEN", "Kiribati": "KIR", "Kuwait": "KWT",
        "Kyrgyzstan": "KGZ", "Laos": "LAO", "Latvia": "LVA",
        "Lebanon": "LBN", "Lesotho": "LSO", "Liberia": "LBR",
        "Libya": "LBY", "Liechtenstein": "LIE", "Lithuania": "LTU",
        "Luxembourg": "LUX", "Madagascar": "MDG", "Malawi": "MWI",
        "Malaysia": "MYS", "Maldives": "MDV", "Mali": "MLI",
        "Malta": "MLT", "Marshall Islands": "MHL", "Mauritania": "MRT",
        "Mauritius": "MUS", "Mexico": "MEX", "Micronesia": "FSM",
        "Moldova": "MDA", "Monaco": "MCO", "Mongolia": "MNG",
        "Montenegro": "MNE", "Morocco": "MAR", "Mozambique": "MOZ",
        "Myanmar": "MMR", "Namibia": "NAM", "Nauru": "NRU",
        "Nepal": "NPL", "Netherlands": "NLD", "New Zealand": "NZL",
        "Nicaragua": "NIC", "Niger": "NER", "Nigeria": "NGA",
        "North Korea": "PRK", "North Macedonia": "MKD", "Norway": "NOR",
        "Oman": "OMN", "Pakistan": "PAK", "Palau": "PLW",
        "Palestine": "PSE", "Panama": "PAN", "Papua New Guinea": "PNG",
        "Paraguay": "PRY", "Peru": "PER", "Philippines": "PHL",
        "Poland": "POL", "Portugal": "PRT", "Qatar": "QAT",
        "Romania": "ROU", "Russia": "RUS", "Rwanda": "RWA",
        "Saint Kitts and Nevis": "KNA", "Saint Lucia": "LCA",
        "Saint Vincent and the Grenadines": "VCT", "Samoa": "WSM",
        "San Marino": "SMR", "Sao Tome and Principe": "STP",
        "Saudi Arabia": "SAU", "Senegal": "SEN", "Serbia": "SRB",
        "Seychelles": "SYC", "Sierra Leone": "SLE", "Singapore": "SGP",
        "Slovakia": "SVK", "Slovenia": "SVN", "Solomon Islands": "SLB",
        "Somalia": "SOM", "South Africa": "ZAF", "South Korea": "KOR",
        "South Sudan": "SSD", "Spain": "ESP", "Sri Lanka": "LKA",
        "Sudan": "SDN", "Suriname": "SUR", "Sweden": "SWE",
        "Switzerland": "CHE", "Syria": "SYR", "Taiwan": "TWN",
        "Tajikistan": "TJK", "Tanzania": "TZA", "Thailand": "THA",
        "Timor-Leste": "TLS", "Togo": "TGO", "Tonga": "TON",
        "Trinidad and Tobago": "TTO", "Tunisia": "TUN", "Turkey": "TUR",
        "Turkmenistan": "TKM", "Tuvalu": "TUV", "Uganda": "UGA",
        "Ukraine": "UKR", "United Arab Emirates": "ARE", "United Kingdom": "GBR",
        "United States": "USA", "Uruguay": "URY", "Uzbekistan": "UZB",
        "Vanuatu": "VUT", "Vatican City": "VAT", "Venezuela": "VEN",
        "Vietnam": "VNM", "Yemen": "YEM", "Zambia": "ZMB",
        "Zimbabwe": "ZWE"
    };



    ngOnInit(): void { }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['dataPorPais']) {
            console.log("DATA PAIS: ", this.dataPorPais)
            this.dibujarMapa();
        }
    }

    public dibujarMapa(): void {
        d3.select("#mapa-d3 svg").remove();

        const svg = d3.select("#mapa-d3").append("svg")
            .attr("width", 960)
            .attr("height", 500);

        const projection = d3.geoNaturalEarth1().fitSize([960, 500], { type: "Sphere" });
        const path = d3.geoPath(projection);

        const maxValor = Math.max(...Object.values(this.dataPorPais), 1);
        const color = d3.scaleLinear<string>()
            .domain([1, maxValor])
            .range(["#cce5ff", "#003366"]); // Azul claro a azul oscuro


        d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json").then((worldData) => {
            const world = worldData as Topology;
            const featureCollection = topojson.feature(
                world,
                world.objects['countries']
            ) as unknown as FeatureCollection<Geometry, GeoJsonProperties>;
            svg.selectAll("path")
                .data(featureCollection.features)
                .join("path")
                .attr("d", path)
                .attr("fill", (d: any) => {
                    const nombre = d.properties.name;
                    const iso3 = this.nombreInglesAISO3[nombre];
                    const val = iso3 ? this.dataPorPais[iso3] : undefined;
                    return val != null ? color(val) : "#ccc";
                })
                .append("title")
                .text((d: any) => {
                    const nombre = d.properties.name;
                    const iso3 = this.nombreInglesAISO3[nombre];
                    return `${nombre}: ${this.dataPorPais[iso3] ?? "Sin datos"}`;
                });



        });
    }

}
