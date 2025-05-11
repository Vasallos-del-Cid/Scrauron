import { Identificable } from "../../core/services/api-service/identificable.model";

export interface Fuente extends Identificable {
  nombre: string;
  tipo: string;
  activa: boolean;
  fecha_alta: Date;
  url: string;
}