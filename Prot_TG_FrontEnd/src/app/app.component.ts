import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms'; // ← Mantenha esta importação
import { CommonModule } from '@angular/common'; // ← Mantenha esta importação
import { CadastroService, Usuario } from './services/cadastro.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
    FormsModule,      // ← Para [(ngModel)]
    CommonModule      // ← Para *ngIf, *ngFor, etc.
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'ProcTG';
  
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