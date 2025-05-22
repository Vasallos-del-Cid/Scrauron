import { Observable } from 'rxjs';

import { Identificable } from './identificable.model';
import { DataService } from './data-service.service';
import { ApiOptions } from './api-options.interface';


/**
 * Clase abstracta que define métodos CRUD genéricos para componentes
 * que manejan datos de tipo T.
 *
 * Permite no tener que implementar los métodos CRUD en cada componente
 * 
 * @field modoEdicion: boolean para indicar si se está en modo edición
 * @field itemSeleccionado: T | null para almacenar el item seleccionado
 * 
 * @abstract cargarDatos(): para cargar los datos
 * @abstract leerUno(): para leer un item
 * @abstract guardar(): para guardar un item
 * @abstract actualizar(): para actualizar un item
 * @abstract borrarSeleccionado() para borrar el item seleccionado
 * 
 * @abstract getSeleccionado(): para obtener el item seleccionado
 * 
 * @typeParam T - Tipo de entidad que debe extender de Identificable (_id obligatorio).
 */
export abstract class CrudAbstractMethodsComponent<T extends Identificable> {
  abstract servicio: DataService<T>;
  abstract getSeleccionado(): T | undefined;

  public itemSeleccionado: T | null = null;
  public modoEdicion = false;

  /**
   * Observable que expone la lista de items reactiva
   *
   * Subscribe a este observable para recibir actualizaciones en tiempo real
   */
  get items$(): Observable<T[]> {
    return this.servicio.items$;
  }

  /**
   * leer la lista de items
   * 
   * @param options Opciones para la llamada a la API
   */
  cargarDatos(options?: ApiOptions<T[]>): void {
    this.servicio.getAll(options);
  }

  /**
   * leer un item por id
   * 
   * @param id id del item a leer
   * @param options 
   */
  leerUno(id: string, options?: ApiOptions<T>): void {
    this.servicio.getOne(id, options);
  }

  /**
   * guardar un item
   * 
   * @param item item a guardar
   * @param options 
   */
  guardar(item: T, options?: ApiOptions<T>): void {
    this.servicio.guardar(item, this.modoEdicion, options );
    this.itemSeleccionado = null;
    this.modoEdicion = false;
  }

  /**
   * actualizar un item
   * 
   * @param id id del item a actualizar
   * @param item item a actualizar Partial<T> para permitir la actualización de solo algunos campos
   * @param options 
   */
  actualizar(id: string, item: Partial<T>, options?: ApiOptions<T>): void {
    this.servicio.update(id ,item, options );
    this.itemSeleccionado = null;
    this.modoEdicion = false;
  }

  /**
   * borrar un item seleccionado segun este seleccionado en el componente
   * 
   * {@link getSeleccionado} para obtener el item seleccionado
   * 
   * @param options Opciones para la llamada a la API
   */
  borrarSeleccionado(options?: ApiOptions<void>): void {
    const seleccionados = this.getSeleccionado();
    if (seleccionados) {
      const item = seleccionados;
      if (item._id) {
        this.servicio.delete(item._id, options);
      }
    }
  }

 
}
