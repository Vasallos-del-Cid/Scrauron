/**
 * ApiOptions interface
 * 
 * Esta interfaz define las opciones que se pueden pasar a los métodos de la clase ApiService, para que se ejecuten despues de la llamada.
 * 
 * @param success Callback que se ejecuta cuando la operación es exitosa.
 * @param failure Callback que se ejecuta cuando la operación falla.
 * @param callback Callback que se ejecuta al finalizar la operación, independientemente de si fue exitosa o no.
 * @param silent Si es verdadero, no se mostrarán mensajes de error.
 * 
 * @template T Tipo de datos que se espera recibir o enviar.
 */

export interface ApiOptions<T> {
  /**
   * metodo que se ejecuta cuando la operación es exitosa
   * 
   * @param data 
   * @returns 
   */
  success?: (data: T) => void;
  /**
   * metodo que se ejecuta cuando la operación falla
   * 
   * @param error 
   * @returns 
   */
  failure?: (error: any) => void;
  /**
   * metodo que se ejecuta al finalizar la operación, independientemente de si fue exitosa o no
   * 
   * @returns 
   */
  callback?: () => void;
  /**
   * si es verdadero, no se mostrarán mensajes de error
   */
  silent?: boolean;
}