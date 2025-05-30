import { Identificable } from "../../core/services/data-service/identificable.model";

export interface Conceptos extends Identificable {
  nombre: string;
  descripcion?: string;
  keywords?: string[];
  publicaciones_relacionadas_ids?: string[];
  // estos se deben agregar en back
  num_menciones?: number;
  usuario_creador?: string;
  num_usuarios?: number;
  fecha_creacion?: string;
  activa?: boolean;
}