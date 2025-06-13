import { Identificable } from "../../../core/services/data-service/identificable.model";

export interface Publicacion extends Identificable {
  titulo: string;
  url?: string;
  fecha?: Date;
  contenido?: string;
  fuente?: string;
  tono?: number;
  pais?: string;
  ciudad_region?: string;
}