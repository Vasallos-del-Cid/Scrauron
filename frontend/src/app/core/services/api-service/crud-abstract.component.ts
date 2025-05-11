import { Observable } from 'rxjs';
import { CrudService } from './crud-service.abstract';
import { ApiOptions } from './api-options.interface';
import { Identificable } from './identificable.model';
// Asegúrate de que esté bien la ruta

export abstract class CrudComponent<T extends Identificable> {
  abstract servicio: CrudService<T>;
  itemSeleccionado: T | null = null;
  modoEdicion = false;

  get items$(): Observable<T[]> {
    return this.servicio.items$;
  }

  cargarDatos(options?: ApiOptions<T[]>): void {
    this.servicio.getAll(options);
  }

  guardar(item: T, options?: ApiOptions<T>): void {
    if (!options) {
      options = {};
    }
    if (!options.success) {
      try {
        options.success = () => {
          alert('🖫 Guardado correctamente');
        };
      } catch (e) {}
    }
    if (this.modoEdicion && item._id) {
      this.servicio.update(item._id, item, options);
    } else {
      this.servicio.create(item, options);
    }
    this.limpiarSeleccion();
  }

  borrar(item: T, options?: ApiOptions<void>): void {
        if (!options) {
      options = {};
    }
    if (!options.success) {
      try {
        options.success = () => {
          alert('🗑 Eliminado correctamente');
        };
      } catch (e) {}
    }
    if (item._id) this.servicio.delete(item._id, options);
    this.limpiarSeleccion();
  }

  seleccionar(item: T): void {
    this.itemSeleccionado = item;
    this.modoEdicion = true;
  }

  limpiarSeleccion(): void {
    this.itemSeleccionado = null;
    this.modoEdicion = false;
  }
}
