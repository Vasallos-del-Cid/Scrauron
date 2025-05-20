import { Identificable } from "../../core/services/data-service/identificable.model";

export interface Areas extends Identificable {
  nombre: string;
  conceptos_interes_ids?: string[];
  fuentes_ids?: string[];
  // estos se deben agregar en back
  usuario_creador?: string;
  fecha_creacion?: string;
  activa?: boolean;
}