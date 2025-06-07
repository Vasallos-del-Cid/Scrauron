export interface ChartConfig {
  selector: string;              // CSS selector o elemento nativo
  data: any[];                   // Datos a graficar
  width: number;
  height: number;
  margin?: { top: number, right: number, bottom: number, left: number };
  [key: string]: any;           // Permite extensibilidad para tipos concretos
}