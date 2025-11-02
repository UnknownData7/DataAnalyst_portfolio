using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ClassLibrary1.Models
{
    public class Product : Subject
    {
        public string? Category { get; set; } //Категория
        public decimal Price { get; set; } //Цена
        public double Quantity { get; set; } //Имеемое количество
        //Переопределенный метод определения эквивалентности объектов Product
        public override bool Equals(object? obj)
        {
            //Определение эквивалентоности по Id
            return this.Id == (obj as Product)?.Id;
        }
        //Переопределение метода преобразования класса в строку
        public override string ToString()
        {
            return $"{Name}, {Price}р, id:{Id} ";
        }
        //Можно не переопределять - используется в словарях
        public override int GetHashCode()
        {
            return Id;
        }
    }

}
