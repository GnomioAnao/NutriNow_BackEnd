// src/app/cadastro/cadastro.component.ts
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { CadastroService, Usuario } from '../services/cadastro.service';

@Component({
  selector: 'app-cadastro',
  standalone: true,
  imports: [FormsModule, CommonModule], // ← Adicione estes imports
  templateUrl: './cadastro.component.html',
  styleUrl: './cadastro.component.css'
})
export class CadastroComponent {
  usuario: Usuario = {
    nome: '',
    sobrenome: '',
    data_nascimento: '',
    genero: '',
    email: '',
    senha: ''
  };

  mensagem: string = '';
  erro: string = '';

  constructor(private cadastroService: CadastroService) {}

  criarConta(): void {
    this.mensagem = '';
    this.erro = '';

    this.cadastroService.criarConta(this.usuario).subscribe({
      next: (response) => {
        this.mensagem = 'Conta criada com sucesso!';
        console.log('Sucesso:', response);
        this.limparFormulario();
      },
      error: (error) => {
        this.erro = error.error?.error || 'Erro ao criar conta';
        console.error('Erro:', error);
      }
    });
  }

  private limparFormulario(): void {
    this.usuario = {
      nome: '',
      sobrenome: '',
      data_nascimento: '',
      genero: '',
      email: '',
      senha: ''
    };
  }
}