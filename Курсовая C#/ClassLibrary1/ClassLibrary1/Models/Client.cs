using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ClassLibrary1.Models
{
    public class Client : Subject
    {
        //Отчество
        public string? FirstName { get; set; }
        //Фамилия
        public string? MiddleName { get; set; }
        //Частное лицо или организация
        public bool IsPerson { get; set; } = true;
        //Переопределение стандартного метода эквивалентности объектов
        public override bool Equals(object? obj)
        {
            return this.Id == (obj as Client)?.Id;
        }
        //Переопределение метода преобразования класса в строку
        public override string ToString()
        {
            return $"{Name}, id:{Id}";
        }
        public override int GetHashCode()
        {
            return this.Id;
        }
    }

}
