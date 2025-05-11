import { BehaviorSubject, Observable } from 'rxjs';
import { ApiService } from './api-service.service';
import { ApiOptions } from './api-options.interface';
import { Identificable } from './identificable.model';

/**
 * Clase abstracta CrudService
 *
 * Esta clase proporciona métodos CRUD (Crear, Leer, Actualizar, Eliminar) para interactuar con una API.
 *
 * Implementa el .subscribe() para manejar la suscripción a los métodos de la API y actualizar el estado interno del servicio.
 *
 * @template T Tipo de datos que se espera recibir o enviar.
 */
export abstract class CrudService<T extends Identificable> {
  /**
   * Subject que almacena el estado interno de los elementos.
   *
   * usa un BehaviorSubject para almacenar el estado interno de los elementos y permitir que los componentes se suscriban a él.
   *
   * @protected
   * @type {BehaviorSubject<T[]>}
   */
  protected readonly _items$ = new BehaviorSubject<T[]>([]);
  /**
   * lista de elementos que se obtiene de la API y se almacena y permite que los componentes puedan suscribirse a ella.
   * 
   * Para represetrla incluir en el html:
   * ```html
   * <ejs-grid
      #grid
      [dataSource]="items$ | async"
      [...]
      >
      ```
   */
  public readonly items$ = this._items$.asObservable();

  /**
   * Constructor de la clase CrudService
   *
   * @param api Instancia del servicio ApiService para realizar las operaciones CRUD.
   */
  constructor(protected api: ApiService<T>) {}

  /**
   * Recupera todos los elementos de la API y actualiza el estado interno.
   *
   * lanza el subscribe().
   * 
   * @param options ApiOptions para ejecutar despues de la llamada HTTP.
   */
  getAll(options?: ApiOptions<T[]>): void {
    this.api
      .getAll({
        ...options,
        success: (data: T[]) => {
          this._items$.next(data);
          options?.success?.(data);
        },
      })
      .subscribe();
  }

  /**
   * Crea un nuevo elemento en la API y actualiza el estado interno.
   *
   * lanza el subscribe().
   * 
   * @param item El elemento a crear
   * @param options ApiOptions para ejecutar despues de la llamada HTTP.
   */
  create(item: T, options?: ApiOptions<T>): void {
    this.api
      .create(item, {
        ...options,
        success: (created: T) => {
          const nuevos = [...this._items$.getValue(), created];
          this._items$.next(nuevos);
          options?.success?.(created);
        },
      })
      .subscribe();
  }

  /**
   * Actualiza un elemento existente en la API y actualiza el estado interno.
   *
   * lanza el subscribe().
   *
   * @param id El ID del elemento a actualizar
   * @param cambios Los cambios a aplicar al elemento (puede ser un objeto parcial)
   * @param options ApiOptions para ejecutar despues de la llamada HTTP.
   */
  update(id: string, cambios: Partial<T>, options?: ApiOptions<T>): void {
    this.api
      .update(id, cambios, {
        ...options,
        success: (updated: T) => {
          const actualizados = this._items$
            .getValue()
            .map((i) => (i._id === id ? updated : i));
          this._items$.next(actualizados);
          options?.success?.(updated);
        },
      })
      .subscribe();
  }

  /**
   * Elimina un elemento de la API y actualiza el estado interno.
   *
   * lanza el subscribe().
   *
   * @param id El ID del elemento a eliminar
   * @param options ApiOptions para ejecutar despues de la llamada HTTP.
   *
   */
  delete(id: string, options?: ApiOptions<void>): void {
    this.api
      .delete(id, {
        ...options,
        success: () => {
          const nuevos = this._items$.getValue().filter((i) => i._id !== id);
          this._items$.next(nuevos);
          options?.success?.();
        },
      })
      .subscribe();
  }

  /**
   * Guarda un elemento en la API, creando uno nuevo o actualizando uno existente.
   *
   * usa el método create o update dependiendo de si se está editando un elemento existente o no.
   * {@link ApiService.create} para crear
   * {@link ApiService.update} para actualizar
   * 
   * @param item El elemento a guardar
   * @param edicion Indica si se está editando un elemento existente
   * @param options ApiOptions para ejecutar despues de la llamada HTTP.
   */
  guardar(item: T, edicion: boolean, options?: ApiOptions<T>): void {
    if (edicion && item._id) {
      this.update(item._id, item, options);
    } else {
      this.create(item, options);
    }
  }
}
