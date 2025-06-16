import { Identificable } from "../../../core/services/data-service/identificable.model";
import { Conceptos } from "../../conceptos/Conceptos.model";
import { Fuente } from "../../fuentes/fuente.model";

export interface Publicacion extends Identificable {
  titulo: string;
  url?: string;
  fecha?: Date;
  contenido?: string;
  fuente?: Fuente;
  tono?: number;
  pais?: string;
  ciudad_region?: string;
  keywords?: { _id: number; nombre: string }[];
  conceptos_relacionados: Conceptos[];
}