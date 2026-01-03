import { Injectable } from '@nestjs/common';
import { CreateTaskDto } from './dto/create-task.dto';
import { UpdateTaskDto } from './dto/update-task.dto';
import { InjectRepository } from '@nestjs/typeorm';
import { Task } from './entities/task.entity';
import { Repository } from 'typeorm';

@Injectable()
export class TasksService {
   constructor(
      @InjectRepository(Task)
      private readonly taskRepository: Repository<Task>
  ) {}
  
  async create(CreateTaskDto: CreateTaskDto) {
    const task = this.taskRepository.create(CreateTaskDto);
    return await this.taskRepository.save(task);
  }


  async findAll(): Promise<Task[]> {
      return await this.taskRepository.find({
    relations: ['project', 'assignee', 'assignedByManager'],
  });
    }

async findone(id: number): Promise<Task | null> {
  return await this.taskRepository.findOne({
    where: { id },
    relations: ['project', 'assignee', 'assignedByManager'],
  });
}
  async findBy(query: object) {
    return await Task.findOne(query);
  }

  async update(id: number, UpdateTaskDto: UpdateTaskDto) {
    await Task.update({ id }, UpdateTaskDto);
    return await Task.findOneBy({ id });
  }

  async remove(id: number) {
    await Task.delete({ id });
    return { deleted: true };
  }
}
