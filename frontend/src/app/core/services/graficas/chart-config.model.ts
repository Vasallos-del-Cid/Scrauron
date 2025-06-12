export interface ChartConfig {
  selector: string; // CSS selector donde se dibuja la gráfica
  data: any[];      // Datos a graficar

  // Dimensiones
  width: number;
  height: number;

  // Margen opcional para espacio alrededor de la gráfica
  margin?: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };

  // Estética
  title?: string;          // Título de la gráfica
  barColor?: string;       // Color de barras (para bar charts)
  lineColor?: string;      // Color de línea (para line charts)
  backgroundColor?: string;// Color de fondo del SVG

  // Ejes
  xField?: string;         // Campo para eje X
  yField?: string;         // Campo para eje Y
  xAxisLabel?: string;     // Etiqueta del eje X
  yAxisLabel?: string;     // Etiqueta del eje Y
  rotateXAxisLabels?: boolean; // Rotar etiquetas del eje X

  // Estilo de texto
  fontSize?: number;
  fontFamily?: string;

  // Tooltips o títulos por barra
  showLabels?: boolean;    // Mostrar etiquetas en barras o puntos

  // Extras
  legend?: boolean;        // Mostrar leyenda
  responsive?: boolean;    // Soporte para adaptar a tamaño del contenedor

  [key: string]: any;      // Extensible para props específicas
  
  yDomain?: [number, number];
}
