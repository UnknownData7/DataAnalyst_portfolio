using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ClassLibrary1.Models
{
    public class Order : Subject
    {
        public DateTime OrderDate { get; set; } //Дата заказа
        public double Quantity { get; set; } //Количество элементов в заказе
        public Product OrderProduct { get; set; } //Заказанный продукт
        public Client OrderClient { get; set; } //Клиент сделавший заказ
        //Переопределение метода установления эквивалентности объектов 
        public override bool Equals(object? obj)
        {
            return this.Id == (obj as Order)?.Id;
        }
        //Переопределение метода преобразования класса в строку
        public override string ToString()
        {
            return $"{OrderClient.Name} - {OrderProduct.Name} : {Quantity} / {OrderDate.Date.ToString("D")}, id:{Id}";
        }
        public override int GetHashCode()
        {
            return this.Id;
        }
    }
}
